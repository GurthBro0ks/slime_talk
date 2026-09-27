package ai.slimy.slimetalk.feasibility
import org.junit.Test
import org.junit.Assert.*
class PTTGateTest {
 @Test fun authorizationRequired(){val g=PTTGate();g.connected();g.press();assertFalse(g.canCapture(0));assertTrue(g.grant(1,0,0));assertTrue(g.canCapture(1));g.stop();assertFalse(g.canCapture(2))}
 @Test fun silenceLatchesUntilRelease(){val g=PTTGate();g.connected();g.press();g.grant(1,0,0);g.captureStarted(0);g.renew(1000,1000);g.renew(2000,2000);assertEquals("silence_expiry",g.expiry(3000));g.stop();assertEquals(PTTGate.State.WAIT_FOR_RELEASE,g.state);assertFalse(g.press());g.release(true);assertTrue(g.press())}
 @Test fun reconnectDoesNotReacquire(){val g=PTTGate();g.connected();g.press();g.grant(1,0,0);g.stop(true);g.connected();assertFalse(g.press());assertFalse(g.canCapture(100));g.release(true);assertTrue(g.press())}
 @Test fun lateGrantAndRenewalRejected(){val g=PTTGate();g.connected();g.press();assertFalse(g.grant(1,0,2000));g.release(true);g.press();g.grant(2,3000,3000);assertFalse(g.renew(4000,5000));assertEquals("authorization_loss",g.expiry(5000))}
}
