from OpenGL.GL import *
import glm

class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.program = glCreateProgram()
        vertex_shader = None
        fragment_shader = None

        if not vertex_path:
            print("No vertex shader")
        else:
            vertex_shader_file = open(vertex_path, "rb")
            vertex_shader_source = vertex_shader_file.read()
            
            vertex_shader = glCreateShader(GL_VERTEX_SHADER)
            glShaderSource(vertex_shader, vertex_shader_source)
            glCompileShader(vertex_shader)

            success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
            if not success:
                print(glGetShaderInfoLog(vertex_shader))
                return
            
            glAttachShader(self.program, vertex_shader)

        if not fragment_path:
            print("No fragment shader")
        else:
            fragment_shader_file = open(fragment_path, "rb")
            fragment_shader_source = fragment_shader_file.read()
             
            fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(fragment_shader, fragment_shader_source)
            glCompileShader(fragment_shader)

            success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
            if not success:
                print(glGetShaderInfoLog(fragment_shader))
                return

            glAttachShader(self.program, fragment_shader)
        
        glLinkProgram(self.program)

        success = glGetProgramiv(self.program, GL_LINK_STATUS)
        if not success:
            print(glGetProgramInfoLog(self.program))
            return
        
        if vertex_shader:
            glDeleteShader(vertex_shader)
        
        if fragment_shader:
            glDeleteShader(fragment_shader)

    def use(self):
        glUseProgram(self.program)
    
    def set_int(self, name: str, value: int):
        location = glGetUniformLocation(self.program, name)
        glUniform1i(location, value)

    def set_float(self, name: str, value: float):
        location = glGetUniformLocation(self.program, name)
        glUniform1f(location, value)

    def set_vec2(self, name: str, value: glm.vec2):
        location = glGetUniformLocation(self.program, name)
        glUniform2f(location, value.x, value.y)

    def set_textures(self, name: str, indices):
        location = glGetUniformLocation(self.program, name)
        glUniform1iv(location, len(indices), indices)

