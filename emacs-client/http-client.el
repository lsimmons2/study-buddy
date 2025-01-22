;;; -*- lexical-binding: t -*-

(defconst api-base-url "localhost:8003")

(defun create-qa-round (file-name success-cb error-cb)
  (message "in create-qa-round")
  (request
    (concat api-base-url "/question-rounds")
    :type "POST"
    :headers '(("Content-Type" . "application/json"))
    :data (json-encode `(("filePath" . ,file-name)))
    :parser 'json-read
    :success (cl-function
	      (lambda (&key data &allow-other-keys)
		(message "in create-qa-round success-cb")
		(funcall success-cb data)))
    :error (cl-function
            (lambda (&key error-thrown response &allow-other-keys)
	      (message "in create-qa-round error-cb")
              (let ((response-body (request-response-data response)))
		(message "Error creating QA round: %s" error-thrown)
		(message "Server response: %s" response-body)
		(funcall error-cb error-thrown))))))

(provide 'http-client)
