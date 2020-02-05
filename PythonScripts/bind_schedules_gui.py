"""Python script for binding a folder of csv output into a multisheet Excel workbook."""

import csv
import os
import os.path
import sys
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import xlwings


class Application(tk.Frame):
    """Main Application Window."""

    DEFAULT_BUTTON_WIDTH = 30
    DEFAULT_BUTTON_HEIGHT = 2

    def __init__(self, master=None):
        """Class Initializer."""
        super().__init__(master)
        self.master = master
        self.master.title("CSV-Binder")
        self.master.minsize(250, 100)
        self.master.resizable(0, 0)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        """Widget Creation Function."""
        self.btn_folder = tk.Button(
            self, text="Bind Folder", command=self.bind_folder,
            width=self.DEFAULT_BUTTON_WIDTH, height=self.DEFAULT_BUTTON_HEIGHT)
        self.btn_folder.pack(side=tk.TOP)
        self.btn_files = tk.Button(
            self, text="Bind Files", command=self.bind_files,
            width=self.DEFAULT_BUTTON_WIDTH, height=self.DEFAULT_BUTTON_HEIGHT)
        self.btn_files.pack(side=tk.TOP)

    def bind_folder(self):
        """Button Command for Binding CSVs from a source folder."""
        source_directory = tkfiledialog.askdirectory(
            title="Select a Folder with CSV Files")
        try:
            csv_file_paths = get_all_csv_files_in_folder(source_directory)
        except IOError as exc:
            print(exc)
            return
        if len(csv_file_paths) < 1:
            print("No files selected, nothing to do.")
            return
        output_filename = tkfiledialog.asksaveasfilename(
            title="Choose Destination Filename",
            defaultextension=".xlsx",
            filetypes=[("Excel-File", ("*.xlsx")),])
        bind_all_files(csv_file_paths, output_filename)

    def bind_files(self):
        """Button Command for Binding a Selection of CSVs."""
        csv_file_paths = tkfiledialog.askopenfilenames(
            title="Select CSV Files",
            filetypes=[("CSV-Files", ("*.csv")),])
        if len(csv_file_paths) < 1:
            print("No files selected, nothing to do.")
            return
        output_filename = tkfiledialog.asksaveasfilename(
            title="Choose Destination Filename",
            defaultextension=".xlsx",
            filetypes=[("Excel-File", ("*.xlsx")),])        
        bind_all_files(csv_file_paths, output_filename)


def get_all_csv_files_in_folder(source_directory):
    """Get all csv file paths of the files contained in a folder."""
    if not os.path.exists(source_directory):
        raise IOError("Given directory path '{path}' does not exist!".format(path=source_directory))
    file_paths = [os.path.join(source_directory, filename) for filename in os.listdir(source_directory)]
    csv_file_paths = [path for path in file_paths if path.endswith(".csv")]
    return csv_file_paths


def bind_all_files(csv_file_paths, output_filename):
    """Main function running the binding logic of the script."""
    workbook = xlwings.Book()
    for csv_file_path in reversed(sorted(csv_file_paths)):
        # Extract important parts of the path and filename
        filename = os.path.basename(csv_file_path)
        _, schedule_code, _ = filename.split("_")
        # Read the CSV file into a python list of lists
        print(f"Reading csv file '{filename}'... ", end="", flush=True)
        title, data = "", []
        with open(csv_file_path, encoding="utf-16") as file:
            reader = csv.reader(file)
            for line, row in enumerate(reader):
                if line == 0:  # title line
                    title = "".join(row)
                else:  # line > 0: data lines
                    data.append(row)
        # Write list data read from the CSV file to the Excel workbook
        print("✔ writing to Excel... ", end="", flush=True)
        current_sheet = workbook.sheets.add(schedule_code)  # create and activate
        current_sheet.range("A1").value = title
        current_sheet.range("A2").value = data
        # Format the sheet
        print("✔ formatting... ", end="", flush=True)
        current_sheet.cells.api.Font.Name = "Arial Narrow"
        current_sheet.cells.api.Font.Size = 10
        current_sheet.range("1:2").api.Font.Bold = True
        current_sheet.autofit()
        print("✔")
    # Delete empty default sheet
    default_sheet = workbook.sheets["Sheet1"]
    default_sheet.delete()
    # Save workbook
    print(f"Saving binder to '{output_filename}'... ", end="", flush=True)
    workbook.save(output_filename)
    workbook.close()
    print("✔")


def main():
    """Main Program."""
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
