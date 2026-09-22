Omni Asset Validator (UI) [omni.asset_validator.ui]
===================================================

Kit UIs for validating assets against Omniverse specific rules to ensure they run smoothly across Omniverse products.

It includes the following components:

- An _Asset Validator Window_ to select rules and run validation on individual USD layer files, recursively search a folder for layer files and validate them all, or validate a live / in-memory `Usd.Stage`, such as the main stage in Kit based applications, for example the USD Composer app template.
- _Content Browser_ context menus to launch the _Asset Validator Window_ preset to the selected file/folder.
- _Layer Window_ context menus to launch the _Asset Validator Window_ preset to either the in-memory layer or the selected layer's file URI.
- _Stage Window_ context menus to launch the _Asset Validator Window_ preset to the currently open stage (i.e. the main stage of the application).

See http://omniverse-docs.s3-website-us-east-1.amazonaws.com/asset-validator for more details.
