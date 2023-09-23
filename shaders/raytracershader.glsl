#version 430

// input/output
// takes in the input in chunks of 8 to speed up the processing
layout(local_size_x = 8, local_size_y = 8) in;
// texture
layout(rgba32f, binding = 0) uniform image2D img_output;



// sphere: center, radius, color
struct Sphere {
    vec3 center;
    float radius;
    vec3 color;
};

// camera: position, forwards, right, up
struct Camera {
    vec3 position;
    vec3 forwards;
    vec3 right;
    vec3 up;
};

// Ray: origin, direction
struct Ray {
    vec3 origin;
    vec3 direction;
};

// renderstate: t(answer from ray-sphere or ray-plane intersection), color, hit(true or false), position(of the ray), ray_normal
struct RenderState{
    float t;
    vec3 color;
    bool hit;
    vec3 position;
    vec3 ray_normal;
};

// plane: center, normal, color, (tangent, bitangent, uMin, uMax, vMin, vMax) -> used to restrict the plane
struct Plane{
    vec3 center;
    vec3 tangent;
    vec3 bitangent;
    vec3 normal;
    float uMin;
    float uMax;
    float vMin;
    float vMax;
    vec3 color;
};
// scene:
// camera input
uniform Camera viewer;
// /////////uniform Sphere spheres[32];
// objects input
layout(rgba32f, binding = 1) readonly uniform image2D objects;
// input number of spheres
uniform float sphereCount;
// input number of planes(can have multiple planes)
uniform float planeCount;

// ===============FUNCTIONS============
// unit vector
vec3 unit_vector(vec3 v);

// color the sphere/ tracing sphere
RenderState RayPath(Ray ray);

// background color (ray tracing in one weekend)
vec3 ray_color(Ray ray);

// function checks if the ray hits the sphere and also returns the ray, position, color and the answer to the ray-sphere equation
RenderState hitsphere(Ray ray, Sphere sphere, float tMin, float tMax, RenderState renderstate );

// function checks if the ray hits the plane and also returns the ray, position, color and the answer to the ray-plane equation
RenderState hitplane(Ray ray, Plane plane, float tMin, float tMax, RenderState renderstate );


// function to get sphere attributes from the texture
Sphere openSphere(int index);

// function to get plane attributes from the texture
Plane openPlane(int index);


void main() {

    ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);
    ivec2 screen_size = imageSize(img_output);

    // coefficients divided by same thing to keep it equal
    float horizontalCoefficient = ((float(pixel_coords.x)*2 - screen_size.x) / screen_size.x ); 
    float verticalCoefficient = ((float(pixel_coords.y)*2 - screen_size.y) / screen_size.x );


// declare a ray with it's origin and direction
    Ray ray;
    ray.origin = viewer.position;
    ray.direction = viewer.forwards + horizontalCoefficient * viewer.right + verticalCoefficient *viewer.up;

// used to change color
    vec3 pixel = vec3(1.0);
    vec3 pixel_color = pixel;

// loop for reflections
    for (int i = 0; i < 16; i++) {

        RenderState renderstate = RayPath(ray);

        if (renderstate.hit == false) {
            // uncomment the line below to see somwthing cool happen
            pixel_color = ray_color(ray);
            break;
        }

        pixel = pixel * renderstate.color;
        pixel_color = pixel;

        ray.origin = renderstate.position;
        ray.direction = reflect(ray.direction, renderstate.ray_normal);

    }
    // vec3 pixel =  RayColor(ray);



    // Sphere sphere;
    // sphere.center = vec3(3.0,0.0,0.0);
    // sphere.radius = 1.0;
    // sphere.color = vec3(1.0,1.0,0.7);


    // float a = dot(ray.direction, ray.direction) ;
    // float b = 2* dot (ray.direction, ray.origin - sphere.center);
    // float c = dot( ray.origin - sphere.center , ray.origin - sphere.center ) - (sphere.radius * sphere.radius);

    // float discriminant = (b * b) - (4 * a * c);

    // if (discriminant > 0) {
    //     pixel = sphere.color;
    // } 

// output color for each pixel
    imageStore(img_output, pixel_coords, vec4(pixel_color,1.0));
}

vec3 unit_vector(vec3 v) {
    return v / sqrt((v.x *v.x)+(v.y * v.y)+(v.z *v.z));
}

vec3 ray_color(Ray ray) {
    Ray r = ray;
    vec3 unit_dir = unit_vector(r.direction);
    // vec3 color = vec3(0.0,1.0,0.0);
    float t = 0.5*(unit_dir.y + 1.0);
    float a = 1.0-t;
    vec3 b = vec3(a*(1.0,1.0,1.0)); 
    vec3 c = vec3(0.5*t,0.7*t,1.0*t);
    vec3 d = b + c;

    return d;
}

RenderState RayPath(Ray ray){

    // vec3 color = ray_color(ray);

    // bool hitSomething = false;
    float nearestHit = 9999999;
    RenderState renderstate;
    renderstate.hit = false;
    renderstate.color = vec3(1.0);

    // loop to check the all the spheres
    for (int i =0; i < sphereCount; i++) {

        RenderState new_renderstate = hitsphere(ray, openSphere(i), 0.001, nearestHit, renderstate);

        if (new_renderstate.hit) {
            nearestHit = new_renderstate.t;
            renderstate = new_renderstate;
        }
    }

    //loop to check all the planes 
    for (int i = int(sphereCount); i < sphereCount + planeCount; i++) {

        RenderState new_renderstate = hitplane(ray, openPlane(i), 0.001, nearestHit, renderstate);

        if (new_renderstate.hit) {
            nearestHit = new_renderstate.t;
            renderstate = new_renderstate;
        }

    }


    return renderstate;
}

RenderState hitsphere(Ray ray, Sphere sphere, float tMin, float tMax, RenderState renderstate ){
    // ray-sphere equation
     vec3 co = ray.origin - sphere.center;
    float a = dot(ray.direction, ray.direction);
    float b = 2 * dot(ray.direction, co);
    float c = dot(co, co) - sphere.radius * sphere.radius;
    float discriminant = b * b - (4 * a * c);

    // check discriminant
    if (discriminant > 0.0) {

    // using only negative sign to get the nearest intersection
        float t = (-b - sqrt(discriminant))/ (2*a);
        
        // store hit as true and other ray values and color if the t value is within range
        if (t > tMin && t < tMax){
            renderstate.t = t;
            renderstate.hit =  true;
            renderstate.color = sphere.color;
            renderstate.position = ray.origin + t * ray.direction;
            renderstate.ray_normal = normalize(renderstate.position - sphere.center);
            return renderstate;
        }
    } 

    renderstate.hit = false;
    return renderstate;
}

RenderState hitplane(Ray ray, Plane plane, float tMin, float tMax, RenderState renderstate ){

    // ray-plane intersection equation
    float denominator = dot (plane.normal, ray.direction);

    // check denominator
    if (denominator < 0.00001){

        float t = dot( plane.center - ray.origin , plane.normal ) / denominator;

        if (t > tMin && t < tMax){

            vec3 testPoint = ray.origin + t * ray.direction;
            vec3 testDirection = testPoint - plane.center;

            // used for restricting the plane
            float u = dot (testPoint, plane.tangent);
            float v = dot(testPoint, plane.bitangent);

            // store ray, the equations answer and color if it is within restrictions
            if (u > plane.uMin && u < plane.uMax && v > plane.vMin && v < plane.vMax) {
                renderstate.t = t;
                renderstate.color = plane.color;
                renderstate.hit = true;
                renderstate.position = testPoint;
                renderstate.ray_normal = plane.normal;

                return renderstate;
            }
        }
    }

    renderstate.hit = false;
    return renderstate;

}

Sphere openSphere(int index){

// c= center, sr = sphere radius
// (cx, cy, cz, sr) (r, g, b, -) (-, -, -, -) (-, -, -, -) (-, -, -, -)
    Sphere sphere;
    vec4 attributeChunk = imageLoad(objects, ivec2(0,index));
    sphere.center = attributeChunk.xyz;
    sphere.radius = attributeChunk.w;
    
    attributeChunk = imageLoad(objects, ivec2(1,index));
    sphere.color = attributeChunk.xyz;

    return sphere;
}

Plane openPlane(int index){

// c= center, pt = plane tangent, pbt = plane bitangent, pn = plane normal
// (cx, cy, cz, ptx) (pty, ptz, pbtx, pbty) (pbtz, pnx, pny, pnz) (puMin, puMax, pvMin, pvMax) (r, g, b, -)
    Plane plane;
    vec4 attributeChunk = imageLoad(objects, ivec2(0,index));
    plane.center = attributeChunk.xyz;
    plane.tangent.x= attributeChunk.w;
    
    attributeChunk = imageLoad(objects, ivec2(1,index));
    plane.tangent.yz = attributeChunk.xy;
    plane.bitangent.xy = attributeChunk.zw;

    attributeChunk = imageLoad(objects, ivec2(2,index));
    plane.bitangent.z = attributeChunk.x;
    plane.normal = attributeChunk.yzw;

    attributeChunk = imageLoad(objects, ivec2(3,index));
    plane.uMin = attributeChunk.x;
    plane.uMax = attributeChunk.y;
    plane.vMin = attributeChunk.z;
    plane.vMax = attributeChunk.w;


    attributeChunk = imageLoad(objects, ivec2(4,index));
    plane.color = attributeChunk.xyz;



    return plane;
}