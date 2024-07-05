# Roadmap to directory

This app import a roadmap from [Roadmap Site](https://roadmap.sh/) into a directory structure.

## Running the Script

You can run the script from the command line:

```bash
python roadmap_extractor.py <roadmap_name> --output <output_directory>
```

This will create the folder structure and markdown files in the specified output directory based on the provided roadmap name.

```bash
python roadmap_extractor.py DevOps --output output
```

## TODO

- Add support for roadmap that belongs to other roadmap, e.g. [Python](https://roadmap.sh/python/) -> [Devops](https://roadmap.sh/devops/). In those cases the structure is different.
