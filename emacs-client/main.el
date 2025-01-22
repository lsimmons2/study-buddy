;;; -*- lexical-binding: t -*-

(require 'http-client)


(define-minor-mode study-buddy-mode
  "Minor mode for working with my study buddy app."
  :lighter "StudyBuddy" ;; Mode indicator in the mode line
  (if study-buddy-mode
      (message "Study Buddy mode activated!")))




(defun study-buddy-qa-current-file ()
  (interactive)
  (message (format "gonna do study buddy qa on file %s" (buffer-name)))
  (let ((notes-file-name (buffer-name)))
    (select-window (split-window-right))
    (switch-to-buffer "*Study Buddy QA*")
    (study-buddy-render-loading)
    (create-qa-round
     notes-file-name
     #'study-buddy-render-success
     #'study-buddy-render-error))
  )

(defun study-buddy-render-loading ()
  "Render a loading message in the current buffer."
  (let ((inhibit-read-only t))
    (erase-buffer)
    (insert "Loading QA data...\n")
    (read-only-mode 1)))


(defun study-buddy-render-success (data)
  (let ((inhibit-read-only t))
    (erase-buffer)
    (insert "QA Data Loaded Successfully:\n\n")
    (mapcar (lambda (qaAttempt)
	      (let ((llmAnswer (alist-get 'llmAnswer qaAttempt))
		    (questionText (alist-get 'questionText qaAttempt)))
		(insert (format "Question:\n%s\n\nLLM Answer:\n%s\n\n" questionText llmAnswer))
		(insert "\n\n\n"))
	      ) (alist-get 'qaAttempts data))
    (read-only-mode 1)))

(defun study-buddy-render-error (error-info)
  "Render the error message in the current buffer.
ERROR-INFO contains details about the error."
  (let ((inhibit-read-only t))
    (erase-buffer)
    (insert "Error Loading QA Data:\n\n")
    (insert (format "%S" error-info))
    (read-only-mode 1)))


(add-hook 'text-mode-hook 'study-buddy-mode)
