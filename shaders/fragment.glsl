#version 330 core
out vec4 fragColor;

uniform vec2 iResolution;
uniform vec2 iViewDirection;
uniform vec2 iPosition;

const int MAP_WIDTH = 24;
const int MAP_HEIGHT = 24;
const int MAP[24 * 24] = int[] (
4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,7,7,7,7,7,7,7,7,
4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7,
4,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,
4,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,
4,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7,
4,0,4,0,0,0,0,5,5,5,5,5,5,5,5,5,7,7,0,7,7,7,7,7,
4,0,5,0,0,0,0,5,0,5,0,5,0,5,0,5,7,0,0,0,7,7,7,1,
4,0,6,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,8,
4,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,7,7,1,
4,0,8,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,8,
4,0,0,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,7,7,7,1,
4,0,0,0,0,0,0,5,5,5,5,0,5,5,5,5,7,7,7,7,7,7,7,1,
6,6,6,6,6,6,6,6,6,6,6,0,6,6,6,6,6,6,6,6,6,6,6,6,
8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,
6,6,6,6,6,6,0,6,6,6,6,0,6,6,6,6,6,6,6,6,6,6,6,6,
4,4,4,4,4,4,0,4,4,4,6,0,6,2,2,2,2,2,2,2,3,3,3,3,
4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2,
4,0,0,0,0,0,0,0,0,0,0,0,6,2,0,0,5,0,0,2,0,0,0,2,
4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2,
4,0,6,0,6,0,0,0,0,4,6,0,0,0,0,0,5,0,0,0,0,0,0,2,
4,0,0,5,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2,
4,0,6,0,6,0,0,0,0,4,6,0,6,2,0,0,5,0,0,2,0,0,0,2,
4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2,
4,4,4,4,4,4,4,4,4,4,1,1,1,2,2,2,2,2,2,3,3,3,3,3
);

const float FOV = 70.0;
const float plane_len = tan(radians(FOV / 2.0));

void main()
{
    vec2 plane_dir = vec2(iViewDirection.y, -iViewDirection.x) * plane_len;

    float uv_x = 2.0 * gl_FragCoord.x / iResolution.x - 1.0;
    vec2 ray_dir = iViewDirection + plane_dir * uv_x;
    ivec2 map_cell = ivec2(iPosition);
    vec2 delta_dist = abs(1.0 / ray_dir);
    ivec2 ray_sign = ivec2(ray_dir.x > 0.0, ray_dir.y > 0.0);
    ivec2 step = ray_sign * 2 - 1;
    vec2 side_dist = vec2(step) * (vec2(map_cell) - iPosition + vec2(ray_sign)) * delta_dist;

    bool hit = false;
    bool side = false;
    
    while (!hit) {
        if (side_dist.x < side_dist.y) {
            side_dist.x += delta_dist.x;
            map_cell.x += step.x;
            side = false;
        }
        else {
            side_dist.y += delta_dist.y;
            map_cell.y += step.y;
            side = true;
        }
        
        hit = MAP[map_cell.y * MAP_WIDTH + map_cell.x] >= 1;
    }
    
    float wall_dist = side_dist.x - delta_dist.x;
    if (side) {
        wall_dist = side_dist.y - delta_dist.y;
    }
    
    int height = int(iResolution.y);
    int line_height = int(iResolution.y / wall_dist);
    int draw_start = max(-line_height / 2 + height / 2, 0);
    int draw_end = min(line_height / 2 + height / 2, height - 1);
    
    vec3 color = vec3(0, 0, 0);
    if (int(gl_FragCoord.y) >= draw_start && int(gl_FragCoord.y) <= draw_end) {
        color = vec3(1, 1, 1);
    }
    if (side) {
        color /= 2.0;
    }

    fragColor = vec4(color, 1.0);
}
