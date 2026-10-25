variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS deployment region"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Target deployment environment (production, staging)"
}

variable "vpc_id" {
  type        = string
  default     = "vpc-0123456789abcdef0"
  description = "VPC ID where the inoculated ASG will reside"
}

variable "subnet_ids" {
  type        = list(string)
  default     = ["subnet-0123456789abcdef0", "subnet-0123456789abcdef1"]
  description = "Subnet IDs for the Auto-Scaling Group"
}

variable "ami_id" {
  type        = string
  default     = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS x86_64
  description = "Base AMI ID for PHP host"
}

variable "instance_type" {
  type        = string
  default     = "t3.medium"
  description = "EC2 instance sizing"
}

variable "desired_capacity" {
  type        = number
  default     = 2
}

variable "min_size" {
  type        = number
  default     = 1
}

variable "max_size" {
  type        = number
  default     = 5
}
