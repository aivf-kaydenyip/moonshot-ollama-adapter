curl \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"inputs":"this is a test prompt, just try say something interesting."}' \
  http://localhost:3100/inference
