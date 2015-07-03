require_relative 'spec_helper'

describe 'the auto scaling group' do
  describe auto_scaling_group('Default-Environment') do
    it { should be_has_desired_capacity 1 }
  end
  describe auto_scaling_group('Default-Environment') do
    it { should be_has_min_size 1 }
  end
  describe auto_scaling_group('Default-Environment') do
    it { should be_has_max_size 4 }
  end
  describe auto_scaling_group('Default-Environment') do
    it { should be_has_launch_configuration 'awseb-e-jfxbzu23eq-stack-AWSEBAutoScalingLaunchConfiguration-9XD6C6TM5B4T' }
  end
  describe auto_scaling_group('Default-Environment') do
    it { should be_has_availability_zone_names ['us-east-1c','us-east-1b','us-east-1a'] }
  end
  describe auto_scaling_group('Default-Environment') do
    it { should be_has_load_balancers ['awseb-e-j-AWSEBLoa-1IZOUQOU0D25E'] }
  end
end
