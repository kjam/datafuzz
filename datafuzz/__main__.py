# -*- coding: utf-8 -*-
""" Call `datafuzz.cli.main` with system arguments"""
import sys

if __name__ == "__main__":
    from datafuzz.cli import main
    main(sys.argv[:])
