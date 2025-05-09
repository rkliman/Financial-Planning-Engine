{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.pandas
    pkgs.python311Packages.numpy  # Optional, remove if unused
    pkgs.python311Packages.matplotlib
    pkgs.python311Packages.seaborn
    pkgs.python311Packages.pylatex

    pkgs.rustc
    pkgs.cargo

    pkgs.rust-analyzer
    pkgs.openssl
    pkgs.pkg-config
    pkgs.graphite2
    pkgs.freetype
    pkgs.icu
    pkgs.libgcc
    pkgs.harfbuzz
    # pkgs.libg

    pkgs.typst
  ];

  shellHook = ''
    export CXXFLAGS="-O2"
  '';
}

