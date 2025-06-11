curl \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"messages":[{"content":"this is a test prompt, just try say something interesting."}]}' \
  http://localhost:5100/inference/mock
echo "\n"
