# -*- coding: utf-8 -*-
"""Minimal standalone GUI for 2D brightfield TIFF segmentation with Cellpose.
Uses fixed segmentation parameters. Processes images sequentially.
"""
from pathlib import Path
import threading
import queue
import traceback
import sys
import json
import subprocess
import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

FLOW = 0.6
CELLPROB = 0.0
PERCENTILES = [1, 99]
JPEG_QUALITY = 95
SETTINGS_FILE = Path(__file__).resolve().with_name('cellpose_simple_local_settings.json')


def saved_python():
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding='utf-8')).get('python_exe', '')
    except (OSError, ValueError, TypeError, AttributeError):
        return ''


def save_python(path):
    try:
        SETTINGS_FILE.write_text(json.dumps({'python_exe': path}, indent=2), encoding='utf-8')
    except OSError:
        pass



def process(input_dir, model_path, output_dir, gpu, events):
    try:
        import numpy as np
        import tifffile
        import imageio.v3 as iio
        from skimage.segmentation import mark_boundaries
        from cellpose import models
        import torch

        files = sorted((p for p in Path(input_dir).iterdir() if p.is_file() and p.suffix.lower() in {'.tif', '.tiff'}), key=lambda p: p.name.lower())
        if not files:
            raise RuntimeError('No TIFF images found in the selected folder (subfolders are not searched).')
        stems = [p.stem.casefold() for p in files]
        if len(stems) != len(set(stems)):
            raise RuntimeError('Two TIFF files share the same base name (.tif/.tiff); rename one to avoid JPEG filename conflicts.')
        if gpu and not torch.cuda.is_available():
            raise RuntimeError('GPU was selected, but PyTorch cannot access CUDA. Disable GPU or configure a CUDA-enabled PyTorch installation.')
        target = Path(output_dir)
        masks_dir = target / 'MasksCell'
        seg_dir = target / 'Segmentation'
        masks_dir.mkdir(parents=True, exist_ok=True)
        seg_dir.mkdir(parents=True, exist_ok=True)
        events.put(('log', 'Loading Cellpose model...'))
        model = models.CellposeModel(gpu=gpu, pretrained_model=model_path)
        events.put(('log', f'TIFF files found: {len(files)}. GPU: {gpu}.'))
        for index, src in enumerate(files, 1):
            mask_path = masks_dir / src.name
            jpg_path = seg_dir / (src.stem + '.jpg')
            if mask_path.exists() or jpg_path.exists():
                raise RuntimeError(f'Output already exists for {src.name}. Choose an empty output folder to prevent overwriting.')
            img = np.squeeze(tifffile.imread(str(src)))
            if img.ndim != 2:
                raise RuntimeError(f'{src.name}: expected a 2D brightfield image, got {img.shape}.')
            result = model.eval([img], flow_threshold=FLOW, cellprob_threshold=CELLPROB,
                                normalize={'percentile': PERCENTILES})
            masks = result[0]
            mask = np.asarray(masks[0])
            if mask.shape != img.shape:
                raise RuntimeError(f'{src.name}: mask shape {mask.shape} does not match image shape {img.shape}.')
            # For previews, preserve uint8 unchanged,
            # otherwise stretch min/max to 0..255.
            if img.dtype == np.uint8:
                gray = img
            else:
                lo, hi = float(np.min(img)), float(np.max(img))
                gray = (np.clip((img.astype(np.float32) - lo) / (hi - lo) * 255.0, 0, 255).astype(np.uint8)
                        if hi > lo else np.zeros(img.shape, dtype=np.uint8))
            rgb = np.stack([gray, gray, gray], axis=2)
            outlined = mark_boundaries(rgb, mask, color=(1, 1, 1), mode='thick')
            outlined = (outlined * 255).clip(0, 255).astype(np.uint8)
            tifffile.imwrite(str(mask_path), mask)
            try:
                iio.imwrite(str(jpg_path), outlined, quality=JPEG_QUALITY)
            except Exception:
                mask_path.unlink(missing_ok=True)
                raise
            events.put(('progress', index, len(files)))
            events.put(('log', f'[{index}/{len(files)}] {src.name} — done'))
        events.put(('done', str(target), len(files)))
    except Exception:
        events.put(('error', traceback.format_exc()))


class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Cellpose Simple — TIFF → MasksCell + Segmentation')
        self.root.geometry('790x540')
        self.events = queue.Queue()
        self.python_exe = tk.StringVar(value=saved_python() or sys.executable)
        self.folder = tk.StringVar()
        self.model = tk.StringVar()
        self.output = tk.StringVar()
        self.gpu = tk.BooleanVar(value=True)
        self.progress = tk.DoubleVar(value=0)
        self.status = tk.StringVar(value='Ready')
        frame = ttk.Frame(root, padding=14)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Simple brightfield TIFF segmentation with Cellpose', font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(frame, text='Python environment (select python.exe with Cellpose installed):').pack(anchor='w', pady=(4, 1))
        env_line = ttk.Frame(frame)
        env_line.pack(fill='x')
        ttk.Entry(env_line, textvariable=self.python_exe).pack(side='left', fill='x', expand=True)
        ttk.Button(env_line, text='Browse...', command=self.browse_python).pack(side='left', padx=(8, 0))
        ttk.Label(frame, text='Select python.exe from your own Cellpose installation.', foreground='#555555').pack(anchor='w', pady=(1, 6))
        for title, variable, is_dir in [
            ('Input TIFF folder:', self.folder, True),
            ('Trained Cellpose model file:', self.model, False),
            ('Output folder (preferably empty):', self.output, True),
        ]:
            ttk.Label(frame, text=title).pack(anchor='w', pady=(6, 1))
            line = ttk.Frame(frame)
            line.pack(fill='x')
            ttk.Entry(line, textvariable=variable).pack(side='left', fill='x', expand=True)
            ttk.Button(line, text='Browse...', command=lambda v=variable, d=is_dir: self.browse(v, d)).pack(side='left', padx=(8, 0))
        ttk.Label(frame, text='Model: BF-CPSAM_1  |  flow=0.6  |  cellprob=0.0  |  normalize=1–99  |  JPEG=95').pack(anchor='w', pady=(14, 4))
        ttk.Checkbutton(frame, text='Use GPU (CUDA)', variable=self.gpu).pack(anchor='w')
        ttk.Label(frame, text='All TIFF files in selected folder; processed one at a time. Subfolders excluded.').pack(anchor='w', pady=(4, 10))
        self.start = ttk.Button(frame, text='Start segmentation', command=self.run)
        self.start.pack(anchor='w')
        ttk.Progressbar(frame, maximum=100, variable=self.progress).pack(fill='x', pady=(12, 2))
        ttk.Label(frame, textvariable=self.status).pack(anchor='w')
        self.log = tk.Text(frame, height=10, wrap='word', state='disabled')
        self.log.pack(fill='both', expand=True, pady=(8, 0))
        self.root.after(120, self.drain)

    def browse_python(self):
        p = filedialog.askopenfilename(title='Select Python executable from a Cellpose environment',
                                       filetypes=[('Python executable', 'python.exe'), ('Executables', '*.exe')])
        if p:
            self.python_exe.set(p)
            save_python(p)

    def browse(self, variable, is_dir):
        path = (filedialog.askdirectory(title='Select folder') if is_dir else
                filedialog.askopenfilename(title='Cellpose model file', filetypes=[('All files', '*.*')]))
        if path:
            variable.set(path)

    def logline(self, msg):
        self.log.configure(state='normal')
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.log.configure(state='disabled')

    def run(self):
        chosen = Path(self.python_exe.get().strip().strip('"'))
        if not chosen.is_file() or chosen.name.lower() not in {'python.exe', 'pythonw.exe'}:
            messagebox.showerror('Python environment', 'Select an existing python.exe from a Cellpose environment.')
            return
        save_python(str(chosen))
        folder, model, output = (x.get().strip() for x in (self.folder, self.model, self.output))
        if not Path(folder).is_dir() or not Path(model).is_file() or not output:
            messagebox.showerror('Missing input', 'Select an existing TIFF folder, a model file, and an output folder.')
            return
        out = Path(output).resolve()
        if out == Path(folder).resolve():
            messagebox.showerror('Choose another folder', 'The output folder must differ from the input folder.')
            return
        if any((out / sub).exists() and any((out / sub).iterdir()) for sub in ('MasksCell', 'Segmentation')):
            messagebox.showerror('Output folder already contains results', 'MasksCell or Segmentation already contains files. Choose an empty output folder.')
            return
        # If opened with another Python, relaunch the exact same GUI with the selected interpreter.
        # Only the selected interpreter needs numpy / Cellpose / PyTorch.
        if chosen.resolve() != Path(sys.executable).resolve():
            cmd = [str(chosen), str(Path(__file__).resolve()), '--autorun',
                   '--input', folder, '--model', model, '--output', output,
                   '--gpu', '1' if self.gpu.get() else '0']
            try:
                subprocess.Popen(cmd, cwd=str(Path(__file__).resolve().parent))
            except OSError as exc:
                messagebox.showerror('Cannot launch selected Python', str(exc))
                return
            self.root.destroy()
            return
        self.start.configure(state='disabled')
        self.progress.set(0)
        self.status.set('Cellpose is running...')
        self.logline('Started. Original TIFF files will not be modified.')
        threading.Thread(target=process, args=(folder, model, output, self.gpu.get(), self.events), daemon=True).start()

    def drain(self):
        try:
            while True:
                evt = self.events.get_nowait()
                if evt[0] == 'log': self.logline(evt[1])
                elif evt[0] == 'progress':
                    self.progress.set(evt[1] / evt[2] * 100)
                    self.status.set(f'Processed: {evt[1]} / {evt[2]}')
                elif evt[0] == 'done':
                    self.start.configure(state='normal')
                    self.status.set(f'Completed: {evt[2]} images')
                    self.logline('Outputs: ' + evt[1])
                    messagebox.showinfo('Completed', f'Images processed: {evt[2]}\n{evt[1]}')
                elif evt[0] == 'error':
                    self.start.configure(state='normal')
                    self.status.set('Error — see the log below')
                    self.logline(evt[1])
                    messagebox.showerror('Cellpose error', 'Processing stopped. See the log for details.')
        except queue.Empty:
            pass
        self.root.after(120, self.drain)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--autorun', action='store_true')
    parser.add_argument('--input', default='')
    parser.add_argument('--model', default='')
    parser.add_argument('--output', default='')
    parser.add_argument('--gpu', default='1')
    args = parser.parse_args()
    window = tk.Tk()
    app = App(window)
    if args.autorun:
        app.python_exe.set(sys.executable)
        app.folder.set(args.input)
        app.model.set(args.model)
        app.output.set(args.output)
        app.gpu.set(args.gpu == '1')
        window.after(350, app.run)
    window.mainloop()
