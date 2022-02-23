// GMSH GEOMETRY FILE FROM MYFEMPY *SECTION RECTANGLE*
SetFactory("OpenCASCADE");
Point(1) = {-0.5,-0.5,0.0};
Point(2) = {0.5,-0.5,0.0};
Point(3) = {0.5,0.5,0.0};
Point(4) = {-0.5,0.5,0.0};
Line(1) = {1,2};
Line(2) = {2,3};
Line(3) = {3,4};
Line(4) = {4,1};
Curve Loop(1) = {1,2,3,4};
Plane Surface(1) = {1};
Transfinite Curve {1,2,3,4} = 10 Using Progression 1;
Transfinite Surface {1};