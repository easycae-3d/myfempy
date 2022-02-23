// GMSH GEOMETRY FILE FROM MYFEMPY
Point(1) = {0,0,0};
Point(2) = {2,0,0};
Point(3) = {2,1,0};
Point(4) = {0,1,0};
Line(1) = {1,2};
Line(2) = {2,3};
Line(3) = {3,4};
Line(4) = {4,1};
Curve Loop(1) = {1,2,3,4};
Plane Surface(1) = {1};
Characteristic Length {1,2,3,4} = 0.05;
//FACE MAPPING 
Transfinite Surface {1};
Mesh.RecombineAll = 1;