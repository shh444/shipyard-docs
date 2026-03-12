@ECHO OFF

set SPHINXBUILD=sphinx-build
set SOURCEDIR=docs
set BUILDDIR=docs\_build

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR%

:end
