{
  description = "Japanese research reports with upLaTeX";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          tex = pkgs.texliveSmall.withPackages (ps: [
            ps.collection-langjapanese
            ps.latexmk
            ps.collection-latexextra
          ]);
        in {
          default = pkgs.mkShell {
            packages = [ tex pkgs.python3 ];
          };
        });
    };
}
