{
  description = "Convert roadmap into a directory structure";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/release-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
        };
        inherit (poetry2nix.lib.mkPoetry2Nix {inherit pkgs;}) mkPoetryApplication defaultPoetryOverrides;
      environment-variable = ''
      '';
      in
        with pkgs; rec {
          devShell = mkShell {
            name = "roadmap_to_dir";
            buildInputs = [
              pkgs.python312
              pkgs.poetry
            ];
            shellHook = ''
              poetry env use ${pkgs.lib.getExe pkgs.python312}
              export VIRTUAL_ENV=$(poetry env info --path)
              export PATH=$VIRTUAL_ENV/bin/:$PATH
              ${environment-variable}
            '';
          };

          # Runtime package with all dependencies using python version as default option.
          packages.app = mkPoetryApplication {
            projectDir = ./.;
            preferWheels = true;
            python = pkgs.python312;
            checkGroups = [];
          };

          # Use xvfb-run to run the bot in headless mode
          packages.bot = pkgs.writeShellScriptBin "roadmap_to_dir" ''
            ${environment-variable}
            ${pkgs.lib.getExe pkgs.xvfb-run} ${packages.app}/bin/roadmap_to_dir
          '';

          formatter = pkgs.alejandra;
        }
    );
}
