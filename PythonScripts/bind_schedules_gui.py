"""Python script for binding a folder of csv output into a multisheet Excel workbook."""

import csv
import os
import os.path
import sys
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import xlwings

# Constants:
SUCCESS = 0
FAILURE = -1


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.btn_files = tk.Button(self, text="Bind Files", command=self.bind_files)
        self.btn_files.pack(side="top")
        self.btn_folder = tk.Button(self, text="Bind Folder", command=self.bind_folder)
        self.btn_folder.pack(side="top")

    def bind_files(self):
        print("bindig files")
        raise NotImplementedError

    def bind_folder(self):
        print("binding folder")
        print("Select Source Folder!")
        source_directory = tkfiledialog.askdirectory()
        print("Choose Destination Filename!")
        output_filename = tkfiledialog.asksaveasfilename()

        bind_all_files(source_directory, output_filename)


def bind_all_files(source_directory, output_filename):
    """Main function running the binding logic of the script."""
    # Check if the given source directory exists
    if not os.path.exists(source_directory):
        print(f"✘ Error: The given path '{source_directory}' does not exist. ")
        return FAILURE
    print(f"Binding files from '{source_directory}'...")
    # Create workbook
    workbook = xlwings.Book()
    # Read CSV files and write them to individual sheets of an Excel workbook
    # Get all files in the source directory and filter for CSV files
    file_paths = [os.path.join(source_directory, filename) for filename in os.listdir(source_directory)]
    csv_file_paths = [path for path in file_paths if path.endswith(".csv")]
    for csv_file_path in reversed(csv_file_paths):
        # Extract important parts of the path and filename
        filename = os.path.basename(csv_file_path)
        _, schedule_code, _ = filename.split("_")
        # Read the CSV file into a python list of lists
        print(f"Reading csv file '{filename}'... ", end="", flush=True)
        title = ""
        data = []
        with open(csv_file_path, encoding="utf-16") as file:
            reader = csv.reader(file)
            for line, row in enumerate(reader):
                if line == 0:  # title line
                    title = "".join(row)
                else:  # line > 0: data lines
                    data.append(row)
        # Write list date read from CSV file to the Excel workbook
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
    # Delete empty default
    default_sheet = workbook.sheets["Sheet1"]
    default_sheet.delete()
    # Save workbook
    binder_output_path = os.path.join(source_directory, output_filename)
    print(f"Saving binder to '{binder_output_path}'... ", end="", flush=True)
    workbook.save(binder_output_path)
    workbook.close()
    print("✔")
    return SUCCESS


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
