import theano
from adt import *
from mnist import *
from ig.util import *
from train import *
from common import *

# theano.config.optimizer = 'Non    e'
theano.config.optimizer = 'fast_compile'


def relation_adt(train_data, options, relation_shape=(1, 28, 28), push_args={},
              pop_args={}, item_shape=(1, 28, 28), batch_size=512, nitems=3):
    """A relation represents a set of statements R(B,L)"""
    # Types
    Relation = Type(relation_shape)
    Item = Type(item_shape)

    # Interface
    union = Interface([Relation, Item], [Relation], 'push', **push_args)
    difference = Interface([Relation], [Relation, Item], 'pop', **pop_args)
    subrelation = Interface([Relation, Relation], [Boolean], 'pop', **pop_args)


    interfaces = [push, pop]

    # train_outs
    train_outs = []
    gen_to_inputs = identity

    # Consts
    empty_relation = Const(Relation)
    consts = [empty_relation]

    # Vars
    # relation1 = ForAllVar(Relation)
    items = [ForAllVar(Item) for i in range(nitems)]
    forallvars = items

    # Axioms
    axioms = []
    batch_empty_relation = repeat_to_batch(empty_relation.input_var, batch_size)
    relation = batch_empty_relation
    for i in range(nitems):
        (relation,) = push(relation, items[i].input_var)
        pop_relation = relation
        for j in range(i, -1, -1):
            (pop_relation, pop_item) = pop(pop_relation)
            axiom = Axiom((pop_item,), (items[j].input_var,))
            axioms.append(axiom)

    # Generators
    generators = [infinite_batches(train_data, batch_size, shuffle=True)
                  for i in range(nitems)]
    train_fn, call_fns = compile_fns(interfaces, consts, forallvars, axioms,
                                     train_outs, options)
    relation_adt = AbstractDataType(interfaces, consts, forallvars, axioms,
                                 name='relation')
    relation_pdt = ProbDataType(relation_adt, train_fn, call_fns, generators,
                             gen_to_inputs, train_outs)
    return relation_adt, relation_pdt


# Validation
def validate_what(data, batch_size, nitems, es, push, pop):
    datalen = data.shape[0]
    es = np.repeat(es, batch_size, axis=0)
    data_indcs = np.random.randint(0, datalen-batch_size, nitems)
    items = [data[data_indcs[i]:data_indcs[i]+batch_size]
             for i in range(nitems)]
    losses = []
    relation = es
    for i in range(nitems):
        (relation,) = push(relation, items[i])
        pop_relation = relation
        for j in range(i, -1, -1):
            (pop_relation, pop_item) = pop(pop_relation)
            loss = mse(pop_item, items[j], tnp=np)
            losses.append(loss)
    print(losses)

def whitenoise_trick():
    new_img = floatX(np.array(np.random.rand(1,1,28,28)*2**8, dtype='int'))/256
    for i in range(1000):
        loss, relation, img, new_relation, new_img = validate_relation(new_img, X_train, push, pop, 0, 512)

def relation_unrelation(n, relation, offrelation=0):
    lb = 0 + offrelation
    ub = 1 + offrelation
    imgs = []
    relations = []
    relations.append(relation)
    for i in range(n):
        new_img = floatX(X_train[lb+i:ub+i])
        imgs.append(new_img)
        (relation,) = push(relation,new_img)
        relations.append(relation)

    for i in range(n):
        (relation, old_img) = pop(relation)
        relations.append(relation)
        imgs.append(old_img)

    return relations + imgs

def whitenoise(batch_size):
    return floatX(np.array(np.random.rand(batch_size,1,28,28)*2**8, dtype='int'))/256


def main(argv):
    # Args
    global options
    global test_files, train_files
    global views, outputs, net
    global push, pop
    global X_train
    global adt, pdt
    global savedir
    global sfx

    cust_options = {}
    cust_options['nitems'] = (int, 3)
    cust_options['width'] = (int, 28)
    cust_options['height'] = (int, 28)
    cust_options['num_epochs'] = (int, 100)
    cust_options['save_every'] = (int, 100)
    cust_options['compile_fns'] = (True,)
    cust_options['save_params'] = (True,)
    cust_options['train'] = (True,)
    cust_options['nblocks'] = (int, 1)
    cust_options['block_size'] = (int, 2)
    cust_options['batch_size'] = (int, 512)
    cust_options['nfilters'] = (int, 24)
    cust_options['layer_width'] = (int, 50)
    cust_options['adt'] = (str, 'relation')
    cust_options['template'] = (str, 'res_net')
    options = handle_args(argv, cust_options)

    X_train, y_train, X_val, y_val, X_test, y_test = load_datarelation()
    sfx = gen_sfx_key(('adt', 'nblocks', 'block_size', 'nfilters'), options)
    options['template'] = parse_template(options['template'])

    adt, pdt = relation_adt(X_train, options, push_args=options,
                         nitems=options['nitems'], pop_args=options,
                         batch_size=options['batch_size'])

    savedir = mk_dir(sfx)
    load_train_save(options, adt, pdt, sfx, savedir)
    push, pop = pdt.call_fns
    loss, relation, img, new_relation, new_img = validate_relation_img_rec(new_img, X_train, push, pop, 0, 1)


if __name__ == "__main__":
    main(sys.argv[1:])
