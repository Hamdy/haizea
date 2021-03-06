from common import BaseSimulatorTest

class TestSimulator(BaseSimulatorTest):
    def __init__(self):
        config = BaseSimulatorTest.load_configfile("base_config_simulator.conf")
        config.set("general", "lease-preparation", "imagetransfer")
        config.set("deploy-imagetransfer", "diskimage-reuse", "image-caches")
        BaseSimulatorTest.__init__(self, config)
   
    def test_preemption(self):
        BaseSimulatorTest.test_preemption(self)
        
    def test_preemption_prematureend(self):
        BaseSimulatorTest.test_preemption_prematureend(self)
        
    def test_preemption_prematureend2(self):
        BaseSimulatorTest.test_preemption_prematureend2(self)

    def test_reservation(self):
        BaseSimulatorTest.test_reservation(self)
        
    def test_reservation_prematureend(self):
        BaseSimulatorTest.test_reservation_prematureend(self)
        
    def test_migrate(self):
        BaseSimulatorTest.test_migrate(self)
        
    def test_reuse1(self):
        BaseSimulatorTest.test_reuse1(self)
        
    def test_reuse2(self):
        BaseSimulatorTest.test_reuse2(self)
        
    def test_wait(self):
        BaseSimulatorTest.test_wait(self)
          