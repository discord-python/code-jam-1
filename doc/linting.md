Linting
=======

Linting is a very important part of maintaining your code. Linting is a process that checks over the
code you've written, looking for common issues and style guide violations.

We require that all of your code be linted. Unlinted code will result in a hefty penalty during our
internal judging process, and we encourage that everyone lints their code before pushing it.

Automatic Linting
-----------------

We use Travis CI to automatically lint code pushed to a pull request. This means that your code will be
checked every time you push it - so we do recommend that you create a pull request as soon as you possibly
can. You can check the status of your commits by going to the page for your pull request - commits with code
that fails to lint will be marked with a red `X`. You can click on that to read the build log, which will
contain all of the errors from the linter - but you should run the linter yourself before pushing to avoid this.

Linting Tooling
---------------

We try to keep the linting process simple, so that users can easily lint their own code. All of our linting is done
by a tool called `flake8`, which you can easily run on your own machine to check your code.

Since our code jams all use Pipenv, you can simply run `pipenv run flake8` to test your code, once you've installed
the project dependencies using `pipenv sync --dev`. If you get no output from this command, congrats - your code
is compliant!

If your code is not compliant, you'll get a stack of error messages which indicate the line number the problem is on,
as well as a description of the problem. Go to the files, fix the issues, and run `flake8` again to ensure that the
problems have been solved.

The validation will seem quite strict at first, but stick with it!

Integration
-----------

Many Python-supporting editors already support basic linting and problem alerting, usually based on the guidelines
provided by the infamous [PEP8](https://www.python.org/dev/peps/pep-0008/). In some cases, however, this will not be
enough.

It's always worth checking whether your editor has a plugin that directly supports `flake8`. Visual Studio Code
[supports Flake8 directly](https://code.visualstudio.com/docs/python/linting), but it needs to be set up using the
`Python: Select Linter` command.

Additionally, you can install a Git hook for `flake8`. This is optional, but it will allow you to have `flake8` run
every time you make a commit. You can do this by running `pipenv run flake8 --install-hook git`.

If you're unsure about editor support, it's always worth googling around and seeing what other users have done to
integrate `flake8`!

---

If you get stuck, don't be afraid to ask for help on the server - but please do take a stab at this yourself first!