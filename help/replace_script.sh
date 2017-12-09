#!/bin/bash
OLDimage="_images\/"
NEWimage="..\/_images\/"
OLDstatic="_static\/"
NEWstatic="..\/_static\/"

LOCALES="en it nl sv fr"

# copy the source folders to the language root folder
cp -r build/html/en/_static build/html/_static
cp -r build/html/en/_images build/html/_images


# remove the language image and static folder
# changhe the paths in each html
for f in $LOCALES
do
  rm -rf build/html/"$f"/_images
  rm -rf build/html/"$f"/_static
  for i in build/html/"$f"/*.html
    do
      sed -i -r "s/$OLDimage/$NEWimage/g" "$i"
      sed -i -r "s/$OLDstatic/$NEWstatic/g" "$i"
    done
done
