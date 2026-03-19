{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.python313.withPackages (ps: with ps; [
            pillow
            click
          ]);
        in
        {
          default = pkgs.mkShell {
            packages = [
              python
              pkgs.imagemagick
              (pkgs.writeShellScriptBin "gifyapper" ''
                exec ${python}/bin/python -m gifyapper.cli "$@"
              '')
            ];

            env.PYTHONPATH = "src";
          };
        });
    };
}
