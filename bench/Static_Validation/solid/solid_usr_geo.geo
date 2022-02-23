// GMSH GEOMETRY FILE FROM MYFEMPY
Point(1) = {0,0,0};
Point(2) = {800,0,0};
Point(3) = {800,80,0};
Point(4) = {0,80,0};
Line(1) = {1,2};
Line(2) = {2,3};
Line(3) = {3,4};
Line(4) = {4,1};
Curve Loop(1) = {1,2,3,4};
Plane Surface(1) = {1};
Characteristic Length {1,2,3,4} = 20;
//FACE MAPPING AND EXTRUDE SURFACE
Transfinite Surface {1};
Recombine Surface {1};
Extrude {0, 0, 80} {Surface{1};Layers{4};Recombine;};