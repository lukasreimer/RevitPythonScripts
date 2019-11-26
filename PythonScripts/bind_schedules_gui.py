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
BUTTON_WIDTH = 30
BUTTON_HEIGHT = 2


class Application(tk.Frame):
    """Main Application Window."""

    def __init__(self, master=None):
        """Class Initializer."""
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        """Widget Creation Function."""
        self.btn_folder = tk.Button(
            self, text="Bind Folder", command=self.bind_folder,
            width=BUTTON_WIDTH, height=BUTTON_HEIGHT,)
        self.btn_folder.pack(side=tk.TOP)
        self.btn_files = tk.Button(
            self, text="Bind Files", command=self.bind_files,
            width=BUTTON_WIDTH, height=BUTTON_HEIGHT,)
        self.btn_files.pack(side=tk.TOP)

    def bind_folder(self):
        """Button Command for Binding CSVs from a source folder."""
        print("Binding folder...")
        print("Select source folder containing CSVs! ", end="")
        source_directory = tkfiledialog.askdirectory(
            title="Select a Folder with CSV Files")
        print("✔")
        print("  ➜ Selected directory: {dir}".format(dir=source_directory))
        print("Checking for CSV files in the folder...", end="")
        csv_file_paths = get_all_csv_files_in_folder(source_directory)
        print("✔")
        print("  ➜ Found {num} CSV files".format(num=len(csv_file_paths)))
        for path in sorted(csv_file_paths):
            print("  ➜ {path}".format(path=path))

        print("Choose Destination Filename! ", end="")
        output_filename = tkfiledialog.asksaveasfilename(
            title="Choose Destination Filename",
            defaultextension=".xlsx",
            filetypes=[("Excel-File", ("*.xlsx")),])
        print("✔")
        print("  ➜ Selected filename: {path}".format(path=output_filename))

        print("Binding CSV files into Excel workbook...")
        bind_all_files(csv_file_paths, output_filename)
        print("Done. 😊")

    def bind_files(self):
        """Button Command for Binding a Selection of CSVs."""
        print("Bindig files...")
        print("Select source files! ", end="")
        csv_file_paths = tkfiledialog.askopenfilenames(
            title="Select CSV Files",
            filetypes=[("CSV-Files", ("*.csv")),])
        print("✔")
        print("  ➜ Selected {num} CSV files".format(num=len(csv_file_paths)))
        for path in sorted(csv_file_paths):
            print("  ➜ {path}".format(path=path))

        print("Choose Destination Filename! ", end="")
        output_filename = tkfiledialog.asksaveasfilename(
            title="Choose Destination Filename",
            defaultextension=".xlsx",
            filetypes=[("Excel-File", ("*.xlsx")),])        
        print("✔")
        print("  ➜ Selected filename: {path}".format(path=output_filename))

        print("Binding CSV files into Excel workbook...")
        bind_all_files(csv_file_paths, output_filename)
        print("Done. 😊")


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
    #binder_output_path = os.path.join(source_directory, output_filename)
    print(f"Saving binder to '{output_filename}'... ", end="", flush=True)
    workbook.save(output_filename)
    workbook.close()
    print("✔")
    return SUCCESS


if __name__ == "__main__":
    root = tk.Tk()
    root.title("CSV-Binder")
    root.minsize(250, 100)
    app = Application(master=root)
    app.mainloop()
