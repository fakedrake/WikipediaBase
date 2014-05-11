;;; Directory Local Variables
;;; See Info node `(emacs) Directory Variables' for more information.

((python-mode
  (fd-python-pre-test-fn . (lambda () (git-commit-all nil)))
  (fd-test-venv . "./remote_test.sh /home/fakedrake/Projects/CSAIL/Python/py/")
  (python-shell-virtualenv-path . "/home/fakedrake/Projects/CSAIL/Python/py/")
  (cs-key . wikipediabase)
  (fd-setup-test-cmd . "test")))
