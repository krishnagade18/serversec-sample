require_relative 'spec_helper'
contents=File.open('properties.txt').read.strip
describe 'the network example' do
  describe vpc(contents) do
    it { should be_default_tenancy }
  end
describe vpc(contents) do
    it { should be_available }
  end

end
