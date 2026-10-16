# Claw
A programming language that compiles to Scratch .sb3 format.

## WORK IN PROGRESS
Claw is no where close to being finished. The codegen has not been added meaning that no .sb3 is generated yet.


### Installation
Run the command below in the project root. The python pip module must be installed.
```
python -m pip install .
```


### Example showing syntax idea
```js

// The standard library directory is searched first, then the current directory
// Meaning if a file with the same name as a standard library file was in the current directory,
// the actual standard library module would take precendence
import "std.math.cw"

// Variables declared at the top level can be accessed throughout the sprite
var x_pos
var y_pos
var dir
var current_costume

// They can additionally be given the global keyword instead to be accessed throughout the entire project (This just marks them "for all sprites")
global sum

fn update_variables() {
  // Reporters are prefixed with the '@' symbol
  x_pos = @x
  y_pos = @y
  dir = @direction
  current_costume = @costume
}

fn update_position(x, y) {
  @x = x
  @y = y
}

fn add3(a, b, c) {
  // Return can have an expression in it or simply be "return"
  // Note a function that has it's return value used but didn't return anything will have
  // the value equivalent to the keyword "None"
  return a + b + c
}

onflag {
  // Calling functions with arguments (both MUST be specified)
  update_position(0, 0)

  // Global variable from earlier
  sum = add3(1, 2, 4)

  // Calling a function without arguments
  update_variables()

  // Some of the reporters are sprite properties that can be changed
  @x = x + 5
  @y = 10
  @costume = "costume2"

  // Builtins are like normal functions
  say(sum)

  wait(@x)

  // Standard library modules are namespaced
  say(math::pow(5, 3))
}

// Namespaces can also be created by the user (additionally they can be nested)
namespace n1 {
  // Anything here is accessed via n1::(thing)
  namespace n2 {
    // Anything here is accessed via n1::n2::(thing)
  }
}
```
