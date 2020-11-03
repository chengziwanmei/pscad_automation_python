# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Power Systems Computer Aided Design (PSCAD)
# ------------------------------------------------------------------------------
#  PSCAD is a powerful graphical user interface that integrates seamlessly
#  with EMTDC, a general purpose time domain program for simulating power
#  system transients and controls in power quality studies, power electronics
#  design, distributed generation, and transmission planning.
#
#  This Python script is a utility class that can be used by end users
#
#
#     PSCAD Support Team <support@pscad.com>
#     Manitoba HVDC Research Centre Inc.
#     Winnipeg, Manitoba. CANADA
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Import dependancies
import shutil, re, os.path

#---------------------------------------------------------------------
# everything_except
#
# Create a filter to be used to exclude file types.
#---------------------------------------------------------------------
def everything_except(*exts):
    """Filter used to exclude the given file types"""

    return lambda _, files: [f for f in files if not any(f.endswith(ext)
                                                         for ext in exts)]

#---------------------------------------------------------------------
# File class
#---------------------------------------------------------------------
class File:

    """File Utilities"""

    #---------------------------------------------------------------------
    # compare_files
    #
    #---------------------------------------------------------------------
    @staticmethod
    def compare_files(file1, file2):
        """Compares two files.  Returns True if the files match"""

        with open(file1) as fp1, open(file2) as fp2:
            # ZIP (like a mechanical zipper, not file compression) the
            # iterators so that a line is returned from each.
            # Call these lines x and y, and test if they are equal.
            # Repeat for ALL lines in the file, AND-ing the results together.
            # Short circuit AND-logic applies; all() will stop at first False.
            files_match = all(x == y for x, y in zip(fp1, fp2))

            # Now check if the file lengths are the same.
            files_match = files_match and next(fp1, None) == None and \
                          next(fp2, None) == None

        return files_match

    #---------------------------------------------------------------------
    # move_files
    #
    # Create a filter to be used to exclude file types.
    #---------------------------------------------------------------------
    @staticmethod
    def move_files(src_dir, dest_dir, *exts):
        """
        Copies files from the source directory to a destination directory.

        The destination directory must not exist; it will be created.
        Only files which match the given extension(s) are copied.
        """

        shutil.copytree(src_dir, dest_dir, ignore=everything_except(*exts))

    #---------------------------------------------------------------------
    # copy_files
    #
    # Copy files from source directory to destination directory.
    #---------------------------------------------------------------------
    @staticmethod
    def copy_files(src_dir, dst_dir, *exts, recursive=False):
        """
        Copies files from the source directory to a destination directory.

        Only files matching the given extensions are copied.  If no
        extensions are given, all files are copied.

        If recursive is True, subdirectories are copied.
        """

        if os.path.exists(dst_dir):
            if not os.path.isdir(dst_dir):
                raise ValueError("Destination is not a directory")
        else:
            os.makedirs(dst_dir)

        for filename in os.listdir(src_dir):
            src = os.path.join(src_dir, filename)
            dst = os.path.join(dst_dir, filename)
            if os.path.isfile(src):
                if not exts or os.path.splitext(filename)[1] in exts:
                    shutil.copy(src, dst)
            elif recursive and os.path.isdir(src):
                File.copy_files(src, dst, *exts, recursive=recursive)

    #---------------------------------------------------------------------
    # copy_file
    #
    # Copy a file to destination directory.
    #---------------------------------------------------------------------
    @staticmethod
    def copy_file(file, dest_dir):
        """Copies a file to the destination directory"""

        shutil.copyfile(file, dest_dir)

    #---------------------------------------------------------------------
    # convert_out_to_csv
    #
    # Converts PSCAD output file to csv.
    #---------------------------------------------------------------------
    @staticmethod
    def convert_out_to_csv(directory, out_file, csv_file):
        """Converts PSCAD output file into a csv file"""

        with open(directory+'\\'+out_file, 'r') as out, \
             open(directory+'\\'+csv_file, 'w') as csv:
            csv.writelines(",".join(line.split())+"\n" for line in out)

#---------------------------------------------------------------------
# OutFile class
#---------------------------------------------------------------------

class OutFile:

    """PSCAD Output file(s) utility class"""

    #---------------------------------------------------------------------
    # Constructor
    #---------------------------------------------------------------------

    def __init__(self, basename):

        """Construct an object which can be used to manipulate a set of
        PSCAD output files (<basename>.inf, <basename>_##.out)
        """

        self._basename = basename       # Save basename of output files
        self._files = None

        self._column = { 'TIME': 0 }    # Column 0 is always "TIME"
        self._column_names = ['TIME']

        self._read_inf()                # Read in the *.inf file


    def _read_inf(self):

        """Read in the *.inf file, and record the PGB descriptions, groups,
        and channel numbers"""

        # Look for 'PGB(##) ... Desc="<desc>" Group="<group>" ...' lines
        inf_re = re.compile(r'^PGB\((\d+)\).+Desc="([^"]+)"\s+Group="([^"]+)"')

        # Open the *.inf file ...
        with open(self._basename + ".inf") as inf:
            # For each line in the file ...
            for line in inf:
                # Test it against the above pattern
                m = inf_re.match(line)
                if m:
                    # If found, extract the column, description and group
                    col = int(m.group(1))
                    desc = m.group(2)
                    grp = m.group(3)

                    # Store the column number under the 'desc' key.
                    self._column[desc] = col
                    if grp:
                        # ... and under the 'group:desc' key.
                        self._column[grp+":"+desc] = col

                    # Store the column description, by column number
                    # (Note: we assume sequential PGB ordering)
                    self._column_names.append(desc)

    #---------------------------------------------------------------------
    # open/close
    #---------------------------------------------------------------------

    def open(self):

        """Open all of the internal data files"""

        if self._files is not None:
            raise IOError("Already open")

        # 1 output file for every 10 channels => #files = ceil(#channels/10)
        # (But don't include the TIME channel in the channel count)
        num_files = (len(self._column_names) + 8) // 10

        # Open up all output files
        filename_fmt = self._basename + "_{:02d}.out"
        filenames = [filename_fmt.format(i+1) for i in range(num_files)]
        self._files = [open(filename) for filename in filenames]

        return self

    def close(self):

        """Close all of the internal data files"""

        if self._files is None:
            raise IOError("Already closed")

        for file in self._files:
            try:
                file.close()
            except Exception as ex:
                print("Failed to close file", file)

        self._files = None

    #---------------------------------------------------------------------
    # Enter/Exit
    #
    # Allow OutFile to be used with the python "with" statement, for proper
    # resource management
    #---------------------------------------------------------------------

    def __enter__(self):

        """Allow OutFile to be treated as a resource in a with statement

        eg)
            with OutFile("basename") as out:
                # use 'out' here

            # 'out' is automatically closed at end of 'with' statement
        """

        self.open()

        return self

    def __exit__(self, type, value, traceback):

        """Close all of the _##.out files"""

        self.close()

    #---------------------------------------------------------------------
    # read_values
    #
    # Return one row of values from each data file, joined together as one
    # list of values.  The time value will only appear once, as the first
    # value
    #---------------------------------------------------------------------

    def read_values(self):

        """Return next row of data, read from all *.out data files"""

        values = None
        # For each file ...
        for file in self._files:
            # ... read one line from each ...
            line = file.readline()
            if not line:
                return None

            # ... split into individual fields
            vals = line.split()
            if values is None:
                # if first file, grab all data, including TIME (column #0)
                values = vals
            else:
                # otherwise, skip the time value, grab the rest
                values.extend(vals[1:])

        return values

    #---------------------------------------------------------------------
    # Iterator
    #
    # Allow an OutFile to be treated as an iterable resource, returning
    # one complete row of data at each iteration.
    #---------------------------------------------------------------------

    def __iter__(self):
        """Returns an iterable object for this OutFile.

        eg)
            for values in out_file:
                time = values[0]
                ch1 = value[1]
                ch2 = value[2]
        """

        return self

    def __next__(self):

        """Return next row of data"""

        values = self.read_values()
        if values is None:
            raise StopIteration

        return values

    #---------------------------------------------------------------------
    # Column name to number
    #---------------------------------------------------------------------

    def column(self, name):

        """Turn a column name into a number"""

        if isinstance(name, int):
            return name

        return self._column[name]

    def column_name(self, column):

        """Turn a column number into a column name"""

        return self._column_names[column]

    #---------------------------------------------------------------------
    # Convert OutFile to CSV
    #---------------------------------------------------------------------

    def toCSV(self, csv=None, columns=None, start=0, end=float("inf")):

        """Convert OutFile into CSV

        If no csv file is specified, defaults to "<basename>.csv".
        If column names are specified, defaults to all columns.
        If start time is given, defaults to start of file.
        If end time is given, defaults to end of file.
        """

        if start < 0:
            raise ValueError("Start must be negative")
        if end <= start:
            raise ValueError("End must be greater than start")

        if csv is None:
            # Default csv filename, if none given
            csv = self._basename+".csv"

        # Determine which columns to export to CSV
        if columns is None:
            # All columns!
            columns = self._column_names
            cols = range(len(columns))
        else:
            # Convert column names into column numbers
            columns = ['TIME'] + list(columns)
            cols = [self.column(name) for name in columns]

        self._toCSV(csv, columns, cols, start, end)

    def _toCSV(self, csv_filename, columns, cols, start, end):

        # Open all "<basename>_##.out" files for input as a closeable resource
        with self as data:

            # Skip header line (from all .out files)
            next(data)

            # Open CSV file for output (as closeable resource)
            with open(csv_filename, 'w') as csv:
                # Write out quoted column names in first row
                csv.write('"' + '", "'.join(columns)+'"\n')

                # Loop over all rows of data
                for values in data:
                    # Convert time value to a number, and check start/end
                    time = float(values[0])
                    if time >= start:
                        if time >= end:
                            break
                        # Write out all values, separated by commas
                        csv.write(', '.join(values[i] for i in cols))
                        csv.write('\n')

# ------------------------------------------------------------------------------
#  End of script
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
