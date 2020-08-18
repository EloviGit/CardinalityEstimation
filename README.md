# CardinalityEstimation

This project focus on compression of HyperLogLog sketch in cardinality estimation.
We aim to find some compression that does not introduce to large variance, easy to update,
and hopefully costs space about its information theoretical limit.

The python scripts runs simulations to compare the performance of our sketches.
By performance, we mean given the same space, how large is the estimation given by those
sketches.

totalling running history and figure files are too large to be uploaded.

### new update: how to simulate 1e20 insertions efficiently.
A fact is, no matter what sketch they is used, the final state of all the sketches are
at least as large as LL do.

In a word, compression means a mapping from all LL states to some other LL states,
and a coding to that. The sketch used must dominate the original LL state, while
we expect they work similarly. At least in terms of thee value of martingale estimator.

Therefore, before everything start, I just test whether that sketch updates LL
if it does not even change LL, then there is no need to ask others
if it does, then we do update function to simulate the process of LL, 

How to simulate the insertions of LL? we do not really need to simulate insertions 
of LL, but we simulate the update of LL; Suppose we are already at (2, 3, 4),
then what would be the next possible state of this LL? it can be (3, 3, 4), 
(2, 6, 4), or (2, 3, 7), whatever. But the point is, we may expect some states like this.

We just randomly choose a counter, and the value of its next state. For example, in this case,
choose one counter from (1, 2, 3), read its value and randomly generate a larger one.
Suppose we generated the first counter and the next value to update: 4

Generally, what is the probability for this random string to happen? 
It is 1/3 * 2^{-4}. But, the probability we would expect an element that cause
update is exactly, the remaining area.

In other words, in the large space of (c, k), when we already have an LL state
(h1, h2, .., hm), we exactly know that, as long as we meet (i, hi+j), where j>0, then
an update happens. If we take all of them as set A, and all the possible strings as U,
then we are randomly sampling in the set U, until we witness an element in A.

This is again, exactly, the geometric distribution of prob(A). We only care about
how many insertions has appeared before the next update, and what this new element is,
therefore, we may just simulate a geometric random variable k and a new element in A.
This process is exactly equivalent to simulate one by one and check whether the new element is in A,
because for those are not in A, you do not care about its actual value; instead, you only
count it as a new element.


### new update: simulation by only the state changes.
For a sketch object, we initialize with the target rounds N. Given that the current state change probability
*a*, we only need to simulate a geometric random variable of *1-a*, or equivalently, an exponential
variable of *1/a*, and accumulate that to *t*, the number of insertions. It can be verified that
the *t* values indicate the time of changes. 

### new update: sampler class
I think there is still something to be improved in the current project. Samplers are itself a class,
but it should be a member of a sketch. That is, not only how the sketch are running, but also 
how its data are collected, should be written together in the very beginning. 
Anyway, I did not do that optimal coding, but used a naive and rather dumb way. But it is enough
for me to use. If anyone would like to improve let him do it.
current tasks only include:

    -logscale sampling: for time from *2^0, 2^0.1, ..., 2^10* sample what is the value of Mtg at the time.
    -onlylast sampling: sample for sample the value in the last iteration
    -fail sample: sample a quantity acrossing many rounds.
