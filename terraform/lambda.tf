locals {
    lambda_function_name = "costume_forecast_bot"
}


# Lambda                                                                       #
data "archive_file" "archive" {
  type        = "zip"
  source_dir  = "../src/lambda_function"
  output_path = "../outputs/lambda_function.zip"
}

resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "tweet_bot.zip"
  layer_name = "lambda_layer_name"

  compatible_runtimes = ["pythin3.11"]
}

resource "aws_lambda_function" "costume_forecast" {
  depends_on = [
    aws_cloudwatch_log_group.lambda,
  ]
  layers = [aws_lambda_layer_version.lambda_layer.arn]
  function_name    = local.lambda_function_name
  filename         = data.archive_file.archive.output_path
  role             = aws_iam_role.lambda.arn
  handler          = "src.lambda_handler"
  source_code_hash = data.archive_file.archive.output_base64sha256
  runtime          = "python3.11"
}



