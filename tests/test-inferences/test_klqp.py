from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import edward as ed
import numpy as np
import tensorflow as tf

from edward.models import Normal


class test_klqp_class(tf.test.TestCase):

  def _test(self, Inference, *args, **kwargs):
    with self.test_session() as sess:
      x_data = np.array([0.0] * 50, dtype=np.float32)

      mu = Normal(loc=0.0, scale=1.0)
      x = Normal(loc=mu, scale=1.0, sample_shape=50)

      qmu_loc = tf.Variable(tf.random_normal([]))
      qmu_scale = tf.nn.softplus(tf.Variable(tf.random_normal([])))
      qmu = Normal(loc=qmu_loc, scale=qmu_scale)

      # analytic solution: N(loc=0.0, scale=\sqrt{1/51}=0.140)
      inference = Inference({mu: qmu}, data={x: x_data})
      inference.run(*args, **kwargs)

      self.assertAllClose(qmu.mean().eval(), 0, rtol=1e-1, atol=1e-1)
      self.assertAllClose(qmu.stddev().eval(), np.sqrt(1 / 51),
                          rtol=1e-1, atol=1e-1)

      variables = tf.get_collection(
          tf.GraphKeys.GLOBAL_VARIABLES, scope='optimizer')
      old_t, old_variables = sess.run([inference.t, variables])
      self.assertEqual(old_t, inference.n_iter)
      sess.run(inference.reset)
      new_t, new_variables = sess.run([inference.t, variables])
      self.assertEqual(new_t, 0)
      self.assertNotEqual(old_variables, new_variables)

  def test_klqp(self):
    self._test(ed.KLqp, n_iter=5000)

  def test_reparameterization_entropy_klqp(self):
    self._test(ed.ReparameterizationEntropyKLqp, n_iter=5000)

  def test_reparameterization_klqp(self):
    self._test(ed.ReparameterizationKLqp, n_iter=5000)

  def test_reparameterization_kl_klqp(self):
    self._test(ed.ReparameterizationKLKLqp, n_iter=5000)

  def test_score_entropy_klqp(self):
    self._test(ed.ScoreEntropyKLqp, n_samples=5, n_iter=5000)

  def test_score_klqp(self):
    self._test(ed.ScoreKLqp, n_samples=5, n_iter=5000)

  def test_score_kl_klqp(self):
    self._test(ed.ScoreKLKLqp, n_samples=5, n_iter=5000)

  def test_score_rb_klqp(self):
    self._test(ed.ScoreRBKLqp, n_samples=5, n_iter=5000)

if __name__ == '__main__':
  ed.set_seed(42)
  tf.test.main()
