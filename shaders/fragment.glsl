#version 330 core
out vec4 fragColor;

uniform vec2 iResolution;
uniform vec2 iViewDirection;
uniform vec2 iPosition;
uniform sampler2D iTextures[8];

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

vec3 floor_cast(vec2 plane_dir) 
{
    // rayDir for leftmost ray (x = 0) and rightmost ray (x = w)
    float ray_dir_x0 = iViewDirection.x - plane_dir.x;
    float ray_dir_y0 = iViewDirection.y - plane_dir.y;
    float ray_dir_x1 = iViewDirection.x + plane_dir.x;
    float ray_dir_y1 = iViewDirection.y + plane_dir.y;

    // Current y position compared to the center of the screen (the horizon)
    float p = gl_FragCoord.y - iResolution.y / 2;

    // Vertical position of the camera.
    float posZ = 0.5 * iResolution.y;

    // Horizontal distance from the camera to the floor for the current row.
    // 0.5 is the z position exactly in the middle between floor and ceiling.
    float rowDistance = abs(posZ / p);

    // calculate the real world step vector we have to add for each x (parallel to camera plane)
    // adding step by step avoids multiplications with a weight in the inner loop
    float floorStepX = rowDistance * (ray_dir_x1 - ray_dir_x0) / iResolution.x;
    float floorStepY = rowDistance * (ray_dir_y1 - ray_dir_y0) / iResolution.x;

    // real world coordinates of the leftmost column. This will be updated as we step to the right.
    float floorX = iPosition.x + rowDistance * ray_dir_x0 + floorStepX * gl_FragCoord.x;
    float floorY = iPosition.y + rowDistance * ray_dir_y0 + floorStepY * gl_FragCoord.x;
    
    // the cell coord is simply got from the integer parts of floorX and floorY
    int cellX = int(floorX);
    int cellY = int(floorY);

    // get the texture coordinate from the fractional part
    float tx = floorX - cellX;
    float ty = floorY - cellY;

    // choose texture and draw the pixel
    int floorTexture = 3;
    int ceilingTexture = 6;
    
    vec3 color = vec3(0, 0, 0);
    // floor
    if (p < 0) {
        color = texture2D(iTextures[floorTexture], vec2(tx, ty) / 2.0).rgb;
    } else {
        color = texture2D(iTextures[ceilingTexture], vec2(tx, ty) / 2.0).rgb;
    }
    return color / 2.0;
}

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
    
    int tex_index = MAP[map_cell.y * MAP_WIDTH + map_cell.x] - 1;
    
    float wall_dist = side_dist.x - delta_dist.x;
    float wall_x = iPosition.y + wall_dist * ray_dir.y;
    if (side) {
        wall_dist = side_dist.y - delta_dist.y;
        wall_x = iPosition.x + wall_dist * ray_dir.x;
    }
    
    wall_x -= floor(wall_x);
    
    int height = int(iResolution.y);
    int line_height = int(iResolution.y / wall_dist);
    int real_draw_start = -line_height / 2 + height / 2;
    int draw_start = max(real_draw_start, 0);
    int draw_end = min(line_height / 2 + height / 2, height - 1);

    vec3 color = floor_cast(plane_dir);
    if (int(gl_FragCoord.y) >= draw_start && int(gl_FragCoord.y) <= draw_end) {
        float wall_y = (gl_FragCoord.y - real_draw_start) / line_height;
 
        vec2 tex_pos = vec2(wall_x, wall_y);
        if ((!side && ray_dir.x > 0) || (side && ray_dir.y < 0)) { 
            tex_pos.x = 1.0 - tex_pos.x;
        }
        color = texture2D(iTextures[tex_index], tex_pos).rgb;
        if (side) {
            color /= 2.0;
        }
    }

    fragColor = vec4(color, 1.0);
}
