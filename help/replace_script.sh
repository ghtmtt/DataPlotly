#!/bin/bash
OLD="_images\/"
NEW="..\/_images\/"
enPATH="build/html/en/*.html"
itPATH="build/html/it/*.html"
nlPATH="build/html/nl/*.html"

echo
echo moving the images directory and removing deprecatd ones ciao
echo

mv build/html/en/_images/ build/html/
rm -rf build/html/it/_images
rm -rf build/html/nl/_images


echo
echo replacing paths in the en dir
echo

for f in $enPATH
do
  sed -i -r "s/$OLD/$NEW/g" "$f"
done

echo
echo replacing paths in the it dir
echo

for f in $itPATH
do
  sed -i -r "s/$OLD/$NEW/g" "$f"
done

echo
echo replacing paths in the nl dir
echo

for f in $nlPATH
do
  sed -i -r "s/$OLD/$NEW/g" "$f"
done
