1)It uses the PIL library to read the image, 
2)then the numpy library to convert to rgb matrix
3)I start by turning the fixed temperature scale into a vector array (top = 350, bottom =-50)
4)Then convert all rgb values into ints (using the rgb2hex function from colormap lib)
5)Then create a linearly spaced vector of same length of temp vals from 350 to -50
|->These correspond with the rgb int vector values
6)I then created a function that would analyze each pixel of an image, find the closest rgbint value in the provided vector and return the corresponding temperature
