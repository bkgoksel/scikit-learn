import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_blobs

from sklearn.utils.class_weight import compute_class_weight
from sklearn.utils.class_weight import compute_sample_weight

from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_true
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_warns


def test_compute_class_weight():
    # Test (and demo) compute_class_weight.
    y = np.asarray([2, 2, 2, 3, 3, 4])
    classes = np.unique(y)
    cw = assert_warns(DeprecationWarning,
                      compute_class_weight, "auto", classes, y)
    assert_almost_equal(cw.sum(), classes.shape)
    assert_true(cw[0] < cw[1] < cw[2])

    cw = compute_class_weight("balanced", classes, y)
    # total effect of samples is preserved
    class_counts = np.bincount(y)[2:]
    assert_almost_equal(np.dot(cw, class_counts), y.shape[0])
    assert_true(cw[0] < cw[1] < cw[2])


def test_compute_class_weight_not_present():
    # Raise error when y does not contain all class labels
    classes = np.arange(4)
    y = np.asarray([0, 0, 0, 1, 1, 2])
    assert_raises(ValueError, compute_class_weight, "auto", classes, y)
    assert_raises(ValueError, compute_class_weight, "balanced", classes, y)


def test_compute_class_weight_invariance():
    # Test that results with class_weight="balanced" is invariant wrt
    # class imbalance if the number of samples is identical.
    # The test uses a balanced two class dataset with 100 datapoints.
    # It creates three versions, one where class 1 is duplicated
    # resulting in 150 points of class 1 and 50 of class 0,
    # one where there are 50 points in class 1 and 150 in class 0,
    # and one where there are 100 points of each class (this one is balanced
    # again).
    # With balancing class weights, all three should give the same model.
    X, y = make_blobs(centers=2, random_state=0)
    # create dataset where class 1 is duplicated twice
    X_1 = np.vstack([X] + [X[y == 1]] * 2)
    y_1 = np.hstack([y] + [y[y == 1]] * 2)
    # create dataset where class 0 is duplicated twice
    X_0 = np.vstack([X] + [X[y == 0]] * 2)
    y_0 = np.hstack([y] + [y[y == 0]] * 2)
    # cuplicate everything
    X_ = np.vstack([X] * 2)
    y_ = np.hstack([y] * 2)
    # results should be identical
    logreg1 = LogisticRegression(class_weight="balanced").fit(X_1, y_1)
    logreg0 = LogisticRegression(class_weight="balanced").fit(X_0, y_0)
    logreg = LogisticRegression(class_weight="balanced").fit(X_, y_)
    assert_array_almost_equal(logreg1.coef_, logreg0.coef_)
    assert_array_almost_equal(logreg.coef_, logreg0.coef_)


def test_compute_class_weight_auto_negative():
    # Test compute_class_weight when labels are negative
    # Test with balanced class labels.
    classes = np.array([-2, -1, 0])
    y = np.asarray([-1, -1, 0, 0, -2, -2])
    cw = assert_warns(DeprecationWarning, compute_class_weight, "auto",
                      classes, y)
    assert_almost_equal(cw.sum(), classes.shape)
    assert_equal(len(cw), len(classes))
    assert_array_almost_equal(cw, np.array([1., 1., 1.]))

    cw = compute_class_weight("balanced", classes, y)
    assert_equal(len(cw), len(classes))
    assert_array_almost_equal(cw, np.array([1., 1., 1.]))

    # Test with unbalanced class labels.
    y = np.asarray([-1, 0, 0, -2, -2, -2])
    cw = assert_warns(DeprecationWarning, compute_class_weight, "auto",
                      classes, y)
    assert_almost_equal(cw.sum(), classes.shape)
    assert_equal(len(cw), len(classes))
    assert_array_almost_equal(cw, np.array([0.545, 1.636, 0.818]), decimal=3)

    cw = compute_class_weight("balanced", classes, y)
    assert_equal(len(cw), len(classes))
    class_counts = np.bincount(y + 2)
    assert_almost_equal(np.dot(cw, class_counts), y.shape[0])
    assert_array_almost_equal(cw, [2. / 3, 2., 1.])


def test_compute_class_weight_auto_unordered():
    # Test compute_class_weight when classes are unordered
    classes = np.array([1, 0, 3])
    y = np.asarray([1, 0, 0, 3, 3, 3])
    cw = assert_warns(DeprecationWarning, compute_class_weight, "auto",
                      classes, y)
    assert_almost_equal(cw.sum(), classes.shape)
    assert_equal(len(cw), len(classes))
    assert_array_almost_equal(cw, np.array([1.636, 0.818, 0.545]), decimal=3)

    cw = compute_class_weight("balanced", classes, y)
    class_counts = np.bincount(y)[classes]
    assert_almost_equal(np.dot(cw, class_counts), y.shape[0])
    assert_array_almost_equal(cw, [2., 1., 2. / 3])


def test_compute_sample_weight():
    # Test (and demo) compute_sample_weight.
    # Test with balanced classes
    y = np.asarray([1, 1, 1, 2, 2, 2])
    sample_weight = assert_warns(DeprecationWarning,
                                 compute_sample_weight, "auto", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])
    sample_weight = compute_sample_weight("balanced", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with user-defined weights
    sample_weight = compute_sample_weight({1: 2, 2: 1}, y)
    assert_array_almost_equal(sample_weight, [2., 2., 2., 1., 1., 1.])

    # Test with column vector of balanced classes
    y = np.asarray([[1], [1], [1], [2], [2], [2]])
    sample_weight = assert_warns(DeprecationWarning,
                                 compute_sample_weight, "auto", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])
    sample_weight = compute_sample_weight("balanced", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with unbalanced classes
    y = np.asarray([1, 1, 1, 2, 2, 2, 3])
    sample_weight = assert_warns(DeprecationWarning,
                                 compute_sample_weight, "auto", y)
    expected_auto = np.asarray([.6, .6, .6, .6, .6, .6, 1.8])
    assert_array_almost_equal(sample_weight, expected_auto)
    sample_weight = compute_sample_weight("balanced", y)
    expected_balanced = np.array([0.7777, 0.7777, 0.7777, 0.7777, 0.7777, 0.7777, 2.3333])
    assert_array_almost_equal(sample_weight, expected_balanced, decimal=4)

    # Test with `None` weights
    sample_weight = compute_sample_weight(None, y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1., 1.])

    # Test with multi-output of balanced classes
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1]])
    sample_weight = assert_warns(DeprecationWarning,
                                 compute_sample_weight, "auto", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])
    sample_weight = compute_sample_weight("balanced", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with multi-output with user-defined weights
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1]])
    sample_weight = compute_sample_weight([{1: 2, 2: 1}, {0: 1, 1: 2}], y)
    assert_array_almost_equal(sample_weight, [2., 2., 2., 2., 2., 2.])

    # Test with multi-output of unbalanced classes
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1], [3, -1]])
    sample_weight = assert_warns(DeprecationWarning,
                                 compute_sample_weight, "auto", y)
    assert_array_almost_equal(sample_weight, expected_auto ** 2)
    sample_weight = compute_sample_weight("balanced", y)
    assert_array_almost_equal(sample_weight, expected_balanced ** 2, decimal=3)


def test_compute_sample_weight_with_subsample():
    # Test compute_sample_weight with subsamples specified.
    # Test with balanced classes and all samples present
    y = np.asarray([1, 1, 1, 2, 2, 2])
    sample_weight = assert_warns(DeprecationWarning,
                                 compute_sample_weight, "auto", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])
    sample_weight = compute_sample_weight("balanced", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with column vector of balanced classes and all samples present
    y = np.asarray([[1], [1], [1], [2], [2], [2]])
    sample_weight = assert_warns(DeprecationWarning,
                                 compute_sample_weight, "auto", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])
    sample_weight = compute_sample_weight("balanced", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with a subsample
    y = np.asarray([1, 1, 1, 2, 2, 2])
    sample_weight = assert_warns(DeprecationWarning,
                                 compute_sample_weight, "auto", y, range(4))
    assert_array_almost_equal(sample_weight, [.5, .5, .5, 1.5, 1.5, 1.5])
    sample_weight = compute_sample_weight("balanced", y, range(4))
    assert_array_almost_equal(sample_weight, [2. / 3, 2. / 3,
                                              2. / 3, 2., 2., 2.])

    # Test with a bootstrap subsample
    y = np.asarray([1, 1, 1, 2, 2, 2])
    sample_weight = assert_warns(DeprecationWarning, compute_sample_weight,
                                 "auto", y, [0, 1, 1, 2, 2, 3])
    expected_auto = np.asarray([1 / 3., 1 / 3., 1 / 3., 5 / 3., 5 / 3., 5 / 3.])
    assert_array_almost_equal(sample_weight, expected_auto)
    sample_weight = compute_sample_weight("balanced", y, [0, 1, 1, 2, 2, 3])
    expected_balanced = np.asarray([0.6, 0.6, 0.6, 3., 3., 3.])
    assert_array_almost_equal(sample_weight, expected_balanced)

    # Test with a bootstrap subsample for multi-output
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1]])
    sample_weight = assert_warns(DeprecationWarning, compute_sample_weight,
                                 "auto", y, [0, 1, 1, 2, 2, 3])
    assert_array_almost_equal(sample_weight, expected_auto ** 2)
    sample_weight = compute_sample_weight("balanced", y, [0, 1, 1, 2, 2, 3])
    assert_array_almost_equal(sample_weight, expected_balanced ** 2)

    # Test with a missing class
    y = np.asarray([1, 1, 1, 2, 2, 2, 3])
    sample_weight = assert_warns(DeprecationWarning, compute_sample_weight,
                                 "auto", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1., 0.])
    sample_weight = compute_sample_weight("balanced", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1., 0.])

    # Test with a missing class for multi-output
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1], [2, 2]])
    sample_weight = assert_warns(DeprecationWarning, compute_sample_weight,
                                 "auto", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1., 0.])
    sample_weight = compute_sample_weight("balanced", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1., 0.])


def test_compute_sample_weight_errors():
    # Test compute_sample_weight raises errors expected.
    # Invalid preset string
    y = np.asarray([1, 1, 1, 2, 2, 2])
    y_ = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1]])
    assert_raises(ValueError, compute_sample_weight, "ni", y)
    assert_raises(ValueError, compute_sample_weight, "ni", y, range(4))
    assert_raises(ValueError, compute_sample_weight, "ni", y_)
    assert_raises(ValueError, compute_sample_weight, "ni", y_, range(4))

    # Not "auto" for subsample
    assert_raises(ValueError,
                  compute_sample_weight, {1: 2, 2: 1}, y, range(4))

    # Not a list or preset for multi-output
    assert_raises(ValueError, compute_sample_weight, {1: 2, 2: 1}, y_)

    # Incorrect length list for multi-output
    assert_raises(ValueError, compute_sample_weight, [{1: 2, 2: 1}], y_)
