#version 430 core


// vertex shader
// process each vertex
layout (location=0) in vec2 vertexPos;

out vec2 fragmentTextureCoordinate;

void main()
{
    gl_Position = vec4(vertexPos, 0.0, 1.0);
    fragmentTextureCoordinate = 0.5 * (vertexPos + vec2(1.0));
    // fragmentTextureCoordinate.y *= -1;
}