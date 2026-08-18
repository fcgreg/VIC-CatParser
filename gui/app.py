"""VIC-CatParser GUI application."""

import os
import queue
import threading
import time
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
import ijson
from tkinterdnd2 import DND_FILES, TkinterDnD

from vic_catparser.service import CancelledError, process_vic

MAX_PREVIEW_MATCHES = 500
PROGRESS_UPDATE_INTERVAL_S = 0.1
QUEUE_EVENTS_PER_TICK = 50
QUEUE_POLL_INTERVAL_MS = 50


class VICCatParserApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.title("Project VIC Category Parser Utility")
        self.geometry("800x720")
        self.minsize(800, 600)

        self._worker_thread: threading.Thread | None = None
        self._cancel_event = threading.Event()
        self._event_queue: queue.Queue = queue.Queue()
        self._last_output_path: Path | None = None
        self._preview_count = 0
        self._total_matches = 0

        self._build_ui()
        self._poll_queue()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="Project VIC JSON file to parse (uncompressed):").grid(
            row=0, column=0, columnspan=3, padx=12, pady=(12, 4), sticky="w"
        )

        self.input_entry = ctk.CTkEntry(
            input_frame, placeholder_text="Select or drop a JSON file"
        )
        self.input_entry.grid(row=1, column=0, columnspan=2, padx=12, pady=(4, 2), sticky="ew")

        ctk.CTkButton(input_frame, text="Browse...", width=100, command=self._browse_input).grid(
            row=1, column=2, padx=12, pady=(4, 2)
        )

        self.drop_label = ctk.CTkLabel(
            input_frame,
            text="(Drag and drop is supported)",
            text_color=("gray40", "gray60"),
        )
        self.drop_label.grid(row=2, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="w")
        self._register_drop_target(input_frame)

        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=1, column=0, padx=16, pady=8, sticky="ew")
        for col in range(4):
            options_frame.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(options_frame, text="Desired Category").grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w")
        self.category_var = ctk.StringVar(value="0")
        self.category_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.category_var,
            values=["0", "1", "2", "3", "4", "5"],
            width=100,
        )
        self.category_menu.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="w")

        ctk.CTkLabel(options_frame, text="Output format").grid(row=0, column=1, padx=12, pady=(12, 4), sticky="w")
        self.format_var = ctk.StringVar(value="json")
        self.format_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.format_var,
            values=["json", "readable", "hashonly"],
            command=self._on_format_change,
        )
        self.format_menu.grid(row=1, column=1, padx=12, pady=(0, 12), sticky="w")

        ctk.CTkLabel(options_frame, text="Hash type (for the 'hashonly' format)").grid(row=0, column=2, padx=12, pady=(12, 4), sticky="w")
        self.hash_var = ctk.StringVar(value="md5")
        self.hash_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.hash_var,
            values=["md5", "sha1", "photodna"],
            state="disabled",
        )
        self.hash_menu.grid(row=1, column=2, padx=12, pady=(0, 12), sticky="w")

        output_frame = ctk.CTkFrame(self)
        output_frame.grid(row=2, column=0, padx=16, pady=8, sticky="ew")
        output_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(output_frame, text="Output file (required when using the GUI application)").grid(
            row=0, column=0, columnspan=3, padx=12, pady=(12, 4), sticky="w"
        )

        self.output_entry = ctk.CTkEntry(
            output_frame,
            placeholder_text="Leave blank to use suggested filename in input folder",
        )
        self.output_entry.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkButton(output_frame, text="Browse...", width=100, command=self._browse_output).grid(
            row=1, column=2, padx=12, pady=(0, 12)
        )

        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=3, column=0, padx=16, pady=8, sticky="ew")

        self.run_button = ctk.CTkButton(action_frame, text="Run", command=self._start_processing)
        self.run_button.pack(side="left", padx=12, pady=12)

        self.cancel_button = ctk.CTkButton(
            action_frame, text="Cancel", command=self._cancel_processing, state="disabled"
        )
        self.cancel_button.pack(side="left", padx=4, pady=12)

        self.open_folder_button = ctk.CTkButton(
            action_frame,
            text="Open output folder",
            command=self._open_output_folder,
            state="disabled",
        )
        self.open_folder_button.pack(side="right", padx=12, pady=12)

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=4, column=0, padx=16, pady=(0, 4), sticky="ew")
        self.grid_rowconfigure(4, weight=0, minsize=20)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.status_label.grid(row=5, column=0, padx=16, pady=(0, 4), sticky="ew")
        self.grid_rowconfigure(5, weight=0, minsize=24)

        results_frame = ctk.CTkFrame(self)
        results_frame.grid(row=6, column=0, padx=16, pady=(4, 16), sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(6, weight=1)

        self.summary_label = ctk.CTkLabel(results_frame, text="Matches (preview):", anchor="w")
        self.summary_label.grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w")

        tree_container = ctk.CTkFrame(results_frame)
        tree_container.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")

        self.preview_tree = ttk.Treeview(
            tree_container,
            columns=("media_id", "category", "md5", "sha1"),
            show="headings",
            height=10,
        )
        self.preview_tree.heading("media_id", text="MediaID")
        self.preview_tree.heading("category", text="Category")
        self.preview_tree.heading("md5", text="MD5")
        self.preview_tree.heading("sha1", text="SHA1")
        self.preview_tree.column("media_id", width=80, stretch=False)
        self.preview_tree.column("category", width=80, stretch=False)
        self.preview_tree.column("md5", width=260)
        self.preview_tree.column("sha1", width=260)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _on_format_change(self, value: str):
        self.hash_menu.configure(state="normal" if value == "hashonly" else "disabled")

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Select VIC JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            self._set_input_path(path)

    def _browse_output(self):
        fmt = self.format_var.get()
        ext = ".json" if fmt == "json" else ".txt"
        path = filedialog.asksaveasfilename(
            title="Save output file",
            defaultextension=ext,
            filetypes=[("All files", "*.*")],
        )
        if path:
            self.output_entry.set(path)

    def _register_drop_target(self, widget):
        """Enable file drag-and-drop on a widget and all of its descendants."""
        try:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._register_drop_target(child)

    def _on_drop(self, event):
        data = event.data.strip()
        if data.startswith("{") and data.endswith("}"):
            paths = self.tk.splitlist(data)
        else:
            paths = [data.strip("{}")]
        if paths:
            self._set_input_path(paths[0])

    def _set_input_path(self, path: str):
        self.input_entry.set(path)
        self._suggest_output_path(path)

    def _suggest_output_path(self, input_path: str):
        if self.output_entry.get().strip():
            return
        input_file = Path(input_path)
        category = self.category_var.get().strip() or "0"
        fmt = self.format_var.get()
        ext = ".json" if fmt == "json" else ".txt"
        suggested = input_file.parent / f"Category{category}{ext}"
        self.output_entry.set(str(suggested))

    def _set_processing_state(self, processing: bool):
        state = "disabled" if processing else "normal"
        self.run_button.configure(state=state)
        self.cancel_button.configure(state="normal" if processing else "disabled")
        if processing:
            self.open_folder_button.configure(state="disabled")

    def _clear_preview(self):
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        self._preview_count = 0
        self._total_matches = 0
        self.summary_label.configure(text="Match preview")

    def _start_processing(self):
        input_path = self.input_entry.get().strip()
        if not input_path:
            messagebox.showerror("Input required", "Please select an uncompressed Project VIC JSON file.")
            return

        if not Path(input_path).exists():
            messagebox.showerror("File not found", f"File not found: {input_path}")
            return

        category = int(self.category_var.get())

        output_path_str = self.output_entry.get().strip()
        if not output_path_str:
            self._suggest_output_path(input_path)
            output_path_str = self.output_entry.get().strip()

        output_file = Path(output_path_str) if output_path_str else None

        self._cancel_event.clear()
        self._clear_preview()
        self._last_output_path = None
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting...")
        self._set_processing_state(True)

        args = {
            "json_file": Path(input_path),
            "category": category,
            "output_format": self.format_var.get(),
            "hash_type": self.hash_var.get(),
            "output_file": output_file,
        }

        self._worker_thread = threading.Thread(
            target=self._run_processing,
            args=(args,),
            daemon=True,
        )
        self._worker_thread.start()

    def _run_processing(self, args: dict):
        last_progress_time = 0.0
        preview_sent = 0

        def status_callback(message: str):
            self._event_queue.put(("status", message))

        def progress_callback(current: int, total: int):
            nonlocal last_progress_time
            now = time.monotonic()
            if current < total and (now - last_progress_time) < PROGRESS_UPDATE_INTERVAL_S:
                return
            last_progress_time = now
            self._event_queue.put(("progress", (current, total)))

        def match_callback(item: dict):
            nonlocal preview_sent
            if preview_sent >= MAX_PREVIEW_MATCHES:
                return
            preview_sent += 1
            self._event_queue.put((
                "match",
                {
                    "MediaID": item.get("MediaID", ""),
                    "Category": item.get("Category", ""),
                    "MD5": item.get("MD5", ""),
                    "SHA1": item.get("SHA1", ""),
                },
            ))

        try:
            result = process_vic(
                **args,
                status_callback=status_callback,
                progress_callback=progress_callback,
                match_callback=match_callback,
                cancel_event=self._cancel_event,
                max_preview_matches=MAX_PREVIEW_MATCHES,
            )
            self._event_queue.put(("done", result))
        except CancelledError:
            self._event_queue.put(("cancelled", None))
        except ijson.JSONError as e:
            self._event_queue.put(("error", f"Invalid JSON file: {e}"))
        except Exception as e:
            self._event_queue.put(("error", str(e)))

    def _cancel_processing(self):
        self._cancel_event.set()
        self.status_label.configure(text="Cancelling...")

    def _poll_queue(self):
        latest_status = None
        latest_progress = None
        terminal_event = None
        handled = 0

        while handled < QUEUE_EVENTS_PER_TICK:
            try:
                event_type, payload = self._event_queue.get_nowait()
            except queue.Empty:
                break
            handled += 1

            if event_type == "status":
                latest_status = payload
            elif event_type == "progress":
                latest_progress = payload
            elif event_type == "match":
                self._add_preview_row(payload)
            elif event_type in ("done", "cancelled", "error"):
                terminal_event = (event_type, payload)
                break

        if latest_status is not None:
            self.status_label.configure(text=latest_status)
        if latest_progress is not None:
            current, total = latest_progress
            if total > 0:
                self.progress_bar.set(current / total)
            self.status_label.configure(text=f"Processing item {current}/{total}...")

        if terminal_event is not None:
            event_type, payload = terminal_event
            if event_type == "done":
                self._on_processing_done(payload)
            elif event_type == "cancelled":
                self._on_processing_cancelled()
            else:
                self._on_processing_error(payload)

        self.after(QUEUE_POLL_INTERVAL_MS, self._poll_queue)

    def _add_preview_row(self, item: dict):
        self._total_matches += 1
        if self._preview_count >= MAX_PREVIEW_MATCHES:
            self.summary_label.configure(
                text=f"Match preview (showing first {MAX_PREVIEW_MATCHES} of {self._total_matches} matches)"
            )
            return

        self._preview_count += 1
        self.preview_tree.insert(
            "",
            "end",
            values=(
                item.get("MediaID", ""),
                item.get("Category", ""),
                item.get("MD5", ""),
                item.get("SHA1", ""),
            ),
        )
        if self._total_matches > MAX_PREVIEW_MATCHES:
            self.summary_label.configure(
                text=f"Match preview (showing first {MAX_PREVIEW_MATCHES} of {self._total_matches} matches)"
            )
        else:
            self.summary_label.configure(text=f"Match preview ({self._total_matches} matches)")

    def _on_processing_done(self, result):
        self.progress_bar.set(1)
        self._set_processing_state(False)

        summary = f"Found {result.matches_found} matches"
        if result.empty_hash_count > 0:
            summary += f" ({result.empty_hash_count} empty hashes omitted)"
        self.status_label.configure(text=summary)

        if result.output_path:
            self._last_output_path = result.output_path
            self.open_folder_button.configure(state="normal")
            self.status_label.configure(text=f"{summary} — saved to {result.output_path}")

        if result.matches_found == 0:
            self.summary_label.configure(text="Match preview (no matches)")
        elif result.matches_found > MAX_PREVIEW_MATCHES:
            self.summary_label.configure(
                text=f"Match preview (showing first {MAX_PREVIEW_MATCHES} of {result.matches_found} matches)"
            )
        else:
            self.summary_label.configure(text=f"Match preview ({result.matches_found} matches)")

    def _on_processing_cancelled(self):
        self._set_processing_state(False)
        self.status_label.configure(text="Processing cancelled.")

    def _on_processing_error(self, message: str):
        self._set_processing_state(False)
        self.status_label.configure(text=f"Error: {message}")
        messagebox.showerror("Processing error", message)

    def _open_output_folder(self):
        if self._last_output_path and self._last_output_path.exists():
            os.startfile(self._last_output_path.parent)


def main():
    app = VICCatParserApp()
    app.mainloop()


if __name__ == "__main__":
    main()
