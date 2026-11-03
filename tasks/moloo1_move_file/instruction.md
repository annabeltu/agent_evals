# Move a file to a new directory

Move `/app/file.py` into a new directory called `/app/new_dir`.

Create the new directory. Preserve the file contents exactly. The result
must be a regular file at `/app/new_dir/file.py`, not a symbolic link, and
`/app/file.py` must no longer exist.