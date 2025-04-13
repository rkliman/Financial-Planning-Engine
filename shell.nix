{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.pandas
    pkgs.python311Packages.numpy  # Optional, remove if unused
    pkgs.python311Packages.matplotlib
    pkgs.python311Packages.seaborn
  ];

  shellHook = ''
    echo "🐍 Python development environment ready!"
  '';
}
