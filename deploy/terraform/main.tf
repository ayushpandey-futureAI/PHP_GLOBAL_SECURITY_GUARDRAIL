/**
 * =============================================================================
 * TERRAFORM INFRASTRUCTURE-AS-CODE: AUTO-INOCULATED PHP FLEET
 * =============================================================================
 * Provisions an AWS Auto-Scaling Group running Ubuntu/Amazon Linux with
 * zero-touch automated inoculation bootstrap injected at initial boot.
 * =============================================================================
 */

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. Security Group for Web Application Tier
resource "aws_security_group" "web_sg" {
  name        = "${var.environment}-php-inoculated-sg"
  description = "Allow HTTP/HTTPS traffic to inoculated PHP fleet"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP Ingress"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS Ingress"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "PHP-Universal-Vaccine"
  }
}

# 2. Inoculated Launch Template
resource "aws_launch_template" "inoculated_template" {
  name_prefix   = "${var.environment}-inoculated-php-"
  image_id      = var.ami_id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.web_sg.id]

  # User Data Cloud-Init Script running 1-Shot Inoculator
  user_data = base64encode(<<-EOF
              #!/bin/bash
              set -e
              echo "[+] Bootstrapping Inoculated PHP Web Node..."
              
              # Install Git and dependencies
              apt-get update -y && apt-get install -y git curl php-fpm nginx

              # Clone the PHP Universal Security Guardrail Repository
              git clone https://github.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL.git /opt/php-vaccine
              
              # Execute 1-Shot Inoculation Needle
              bash /opt/php-vaccine/scripts/inoculate.sh
              
              echo "[+] Server Inoculation Complete. Active Defense Enabled."
              EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name        = "${var.environment}-inoculated-node"
      Vaccinated  = "True"
      GuardrailVer= "1.3.0"
    }
  }
}

# 3. Auto-Scaling Group
resource "aws_autoscaling_group" "asg" {
  name_prefix         = "${var.environment}-asg-"
  vpc_zone_identifier = var.subnet_ids
  desired_capacity    = var.desired_capacity
  max_size            = var.max_size
  min_size            = var.min_size

  launch_template {
    id      = aws_launch_template.inoculated_template.id
    version = "$Latest"
  }

  health_check_type         = "EC2"
  health_check_grace_period = 300

  tag {
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }
}
