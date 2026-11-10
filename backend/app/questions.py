import re
import json
from typing import List, Dict, Any, Optional, Set
from sqlalchemy import or_
from backend.app.database import SessionLocal
import backend.app.models as models
from nlp.answer_analyzer import extract_key_concepts

# Multi-Domain Structured Question Bank with Complete Evaluation Specifications
TECH_QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
    "python": [
        {
            "id": 101,
            "question": "In Python, how does the Global Interpreter Lock (GIL) affect multithreaded CPU-bound tasks versus I/O-bound tasks, and how do you achieve true parallelism?",
            "topic": "Python Internals & Concurrency",
            "category": "Python Deep Dive",
            "difficulty": "Hard",
            "expected_answer": "The Python GIL is a mutex that prevents multiple native threads from executing Python bytecodes simultaneously. For I/O-bound tasks, threads release the GIL during blocking operations, making threading or asyncio effective. For CPU-bound tasks, true parallelism requires multiprocessing, process pools, or C extensions that run outside the GIL.",
            "reference_answer": "The Python GIL is a mutex that prevents multiple native threads from executing Python bytecodes simultaneously. For I/O-bound tasks, threads release the GIL during blocking operations, making threading or asyncio effective. For CPU-bound tasks, true parallelism requires multiprocessing, process pools, or C extensions that run outside the GIL.",
            "required_concepts": ["gil", "mutex", "cpu-bound", "i/o-bound", "multiprocessing"],
            "optional_concepts": ["asyncio", "c extensions", "process pool", "threads release gil", "bytecode"],
            "acceptable_alternatives": ["Using Cython/C-types or nogil in Cython", "Celery or distributed workers for CPU jobs", "subinterpreters (PEP 684)"],
            "common_misconceptions": [
                "Thinking Python threads provide multi-core parallel speedup for heavy math/CPU computation",
                "Claiming asyncio bypasses the GIL for CPU-bound tasks without separate processes",
                "Assuming the GIL prevents all race conditions in user-level code"
            ],
            "rubric": {
                "explains_gil_mutex": 25,
                "distinguishes_io_vs_cpu": 30,
                "identifies_multiprocessing_solution": 30,
                "mentions_gil_release_or_alternatives": 15
            },
            "follow_up_criteria": "If candidate mentions threading but omits multiprocessing, ask how CPU cores are utilized.",
            "targetTime": "60-90 sec",
            "track": "Python Track"
        },
        {
            "id": 102,
            "question": "What is the difference between Python list comprehensions and generators, and how does memory usage differ between them when processing large datasets?",
            "topic": "Python Data Structures & Memory",
            "category": "Python Fundamentals",
            "difficulty": "Medium",
            "expected_answer": "List comprehensions compute and store all elements eagerly in memory, returning a full list with O(N) memory allocation. Generators compute values lazily on demand using the yield keyword or generator expressions, maintaining state with O(1) memory complexity.",
            "reference_answer": "List comprehensions compute and store all elements eagerly in memory, returning a full list with O(N) memory allocation. Generators compute values lazily on demand using the yield keyword or generator expressions, maintaining state with O(1) memory complexity.",
            "required_concepts": ["eager", "lazy", "yield", "memory", "o(1) vs o(n)"],
            "optional_concepts": ["next()", "generator expression", "iterator protocol", "iterable", "streaming"],
            "acceptable_alternatives": ["Explaining via iterator protocol __iter__ and __next__", "Streaming chunks using itertools"],
            "common_misconceptions": [
                "Assuming generators cache previous values once yielded",
                "Thinking list comprehensions are always faster than generators for streaming data"
            ],
            "rubric": {
                "eager_vs_lazy_evaluation": 35,
                "memory_complexity_distinction": 35,
                "yield_syntax_or_iterator_protocol": 30
            },
            "follow_up_criteria": "Ask how to chain multiple generators together with itertools.",
            "targetTime": "45-90 sec",
            "track": "Python Track"
        },
        {
            "id": 103,
            "question": "How do Python decorators work under the hood, and how can you preserve the original function's metadata using functools.wraps?",
            "topic": "Python Metaprogramming & Closures",
            "category": "Python Fundamentals",
            "difficulty": "Medium",
            "expected_answer": "Decorators are higher-order functions that accept a callable, wrap its execution with additional behavior inside a closure, and return the wrapped function. functools.wraps is a decorator that copies the original function's __name__, __doc__, and __annotations__ onto the wrapper to prevent metadata erasure.",
            "reference_answer": "Decorators are higher-order functions that accept a callable, wrap its execution with additional behavior inside a closure, and return the wrapped function. functools.wraps is a decorator that copies the original function's __name__, __doc__, and __annotations__ onto the wrapper to prevent metadata erasure.",
            "required_concepts": ["higher-order function", "closure", "wrapper", "functools.wraps", "metadata"],
            "optional_concepts": ["__name__", "__doc__", "introspection", "*args", "**kwargs"],
            "acceptable_alternatives": ["Manually copying __dict__ or attributes using update_wrapper"],
            "common_misconceptions": [
                "Thinking decorators alter the compiled bytecode of the decorated function directly",
                "Forgetting that omitting @wraps causes introspection tools and debuggers to see the wrapper name"
            ],
            "rubric": {
                "closure_and_callable_wrapping": 40,
                "purpose_of_functools_wraps": 40,
                "metadata_preservation_details": 20
            },
            "follow_up_criteria": "Ask how to implement a decorator that takes custom configuration arguments.",
            "targetTime": "45-90 sec",
            "track": "Python Track"
        }
    ],
    "django": [
        {
            "id": 201,
            "question": "In Django ORM, what is the 'N+1 query problem', and how do select_related and prefetch_related solve it?",
            "topic": "Django ORM Optimization",
            "category": "Django Architecture",
            "difficulty": "Hard",
            "expected_answer": "The N+1 query problem occurs when an application executes 1 query for N parent records, then N separate queries to fetch related objects inside a loop. select_related performs a SQL JOIN for single-valued relationships (ForeignKey, OneToOne) in a single query. prefetch_related executes a separate query with an IN clause for multi-valued relationships (ManyToMany, reverse ForeignKey) and joins them in Python.",
            "reference_answer": "The N+1 query problem occurs when an application executes 1 query for N parent records, then N separate queries to fetch related objects inside a loop. select_related performs a SQL JOIN for single-valued relationships (ForeignKey, OneToOne) in a single query. prefetch_related executes a separate query with an IN clause for multi-valued relationships (ManyToMany, reverse ForeignKey) and joins them in Python.",
            "required_concepts": ["n+1 query", "select_related", "prefetch_related", "sql join", "many-to-many vs foreignkey"],
            "optional_concepts": ["django debug toolbar", "in clause", "python join", "one-to-one", "queryset evaluation"],
            "acceptable_alternatives": ["Using Prefetch objects for filtered prefetches", "annotate or Subquery expressions"],
            "common_misconceptions": [
                "Thinking select_related works on ManyToMany relationships (it only handles single-valued ForeignKeys)",
                "Assuming Django ORM automatically batches relational queries without explicit prefetching"
            ],
            "rubric": {
                "explains_n_plus_one_mechanism": 30,
                "select_related_sql_join_rule": 35,
                "prefetch_related_batch_in_rule": 35
            },
            "follow_up_criteria": "Ask how to apply a filter on prefetched models using Prefetch().",
            "targetTime": "60-90 sec",
            "track": "Django Track"
        },
        {
            "id": 202,
            "question": "How does Django's request-response lifecycle process middleware, and how would you implement custom middleware for authentication or request timing?",
            "topic": "Django Lifecycle & Middleware",
            "category": "Django Architecture",
            "difficulty": "Medium",
            "expected_answer": "Django processes middleware in top-down order during the request phase and reverse bottom-up order during the response phase. A custom middleware class implements __init__(get_response) and __call__(request), recording state before get_response(request) and after to inject headers or log timing.",
            "reference_answer": "Django processes middleware in top-down order during the request phase and reverse bottom-up order during the response phase. A custom middleware class implements __init__(get_response) and __call__(request), recording state before get_response(request) and after to inject headers or log timing.",
            "required_concepts": ["request lifecycle", "get_response", "__call__", "order in settings.py", "pre and post processing"],
            "optional_concepts": ["process_view", "process_exception", "response modification", "http response"],
            "acceptable_alternatives": ["Function-based middleware closures instead of class-based middleware"],
            "common_misconceptions": [
                "Thinking middleware responses execute in the same order as request dispatch",
                "Assuming middleware cannot short-circuit the request before hitting the view"
            ],
            "rubric": {
                "order_of_execution_explained": 35,
                "middleware_structure_get_response": 35,
                "practical_timing_or_auth_example": 30
            },
            "follow_up_criteria": "Ask how to handle exceptions globally with process_exception.",
            "targetTime": "45-90 sec",
            "track": "Django Track"
        }
    ],
    "fastapi": [
        {
            "id": 301,
            "question": "How does FastAPI achieve high performance using Python asyncio and Starlette, and what is the difference between defining path operations with 'async def' versus standard 'def'?",
            "topic": "FastAPI Async Architecture",
            "category": "FastAPI Architecture",
            "difficulty": "Hard",
            "expected_answer": "FastAPI uses Starlette and Pydantic on top of an ASGI server like Uvicorn. Endpoints declared with 'async def' run directly on the asyncio event loop for non-blocking I/O. Endpoints declared with standard 'def' are automatically run in an external thread pool by AnyIO so blocking calls do not freeze the event loop.",
            "reference_answer": "FastAPI uses Starlette and Pydantic on top of an ASGI server like Uvicorn. Endpoints declared with 'async def' run directly on the asyncio event loop for non-blocking I/O. Endpoints declared with standard 'def' are automatically run in an external thread pool by AnyIO so blocking calls do not freeze the event loop.",
            "required_concepts": ["asgi", "event loop", "async def", "thread pool", "blocking i/o"],
            "optional_concepts": ["starlette", "pydantic", "uvicorn", "anyio", "concurrency"],
            "acceptable_alternatives": ["Using run_in_threadpool explicitly inside async def"],
            "common_misconceptions": [
                "Thinking standard def blocks the entire server (FastAPI offloads it to threads)",
                "Putting blocking synchronous code (like time.sleep or synchronous requests) inside async def, which freezes the event loop"
            ],
            "rubric": {
                "asgi_event_loop_explanation": 30,
                "async_def_nonblocking_behavior": 35,
                "standard_def_threadpool_behavior": 35
            },
            "follow_up_criteria": "Ask what happens if someone calls time.sleep(5) inside an async def endpoint.",
            "targetTime": "60-90 sec",
            "track": "FastAPI Track"
        },
        {
            "id": 302,
            "question": "How does FastAPI's dependency injection system (Depends) facilitate authentication, database session management, and code reusability?",
            "topic": "FastAPI Dependency Injection",
            "category": "FastAPI Architecture",
            "difficulty": "Medium",
            "expected_answer": "FastAPI's Depends allows declaring hierarchical, reusable dependencies. It resolves parameters, handles setup and teardown (yielding a SQLAlchemy database session and closing it in finally), and verifies security credentials before executing route handlers.",
            "reference_answer": "FastAPI's Depends allows declaring hierarchical, reusable dependencies. It resolves parameters, handles setup and teardown (yielding a SQLAlchemy database session and closing it in finally), and verifies security credentials before executing route handlers.",
            "required_concepts": ["depends", "dependency injection", "yield", "teardown/cleanup", "authentication/security"],
            "optional_concepts": ["oauth2", "sqlalchemy session", "sub-dependencies", "unit testing overrides"],
            "acceptable_alternatives": ["Using app.dependency_overrides for mock testing"],
            "common_misconceptions": [
                "Assuming dependencies cannot depend on other dependencies",
                "Forgetting that yield dependencies guarantee cleanup even if an exception occurs"
            ],
            "rubric": {
                "explains_di_parameter_resolution": 35,
                "explains_yield_session_teardown": 35,
                "security_or_reusability_benefits": 30
            },
            "follow_up_criteria": "Ask how to override dependencies during unit testing with pytest.",
            "targetTime": "45-90 sec",
            "track": "FastAPI Track"
        }
    ],
    "java": [
        {
            "id": 401,
            "question": "In Java, how does the JVM manage memory between the Heap and Stack, and how do generational garbage collectors like G1 manage object lifecycles?",
            "topic": "JVM Memory & Garbage Collection",
            "category": "Java Architecture",
            "difficulty": "Hard",
            "expected_answer": "The Stack stores thread-specific primitive variables and method call stack frames. The Heap stores all shared object instances and class data. Generational GC divides the heap into Young Generation (Eden and Survivor spaces) and Old Generation. Minor GCs quickly reclaim short-lived objects in Young Gen; surviving objects are promoted to Old Gen where major GCs run.",
            "reference_answer": "The Stack stores thread-specific primitive variables and method call stack frames. The Heap stores all shared object instances and class data. Generational GC divides the heap into Young Generation (Eden and Survivor spaces) and Old Generation. Minor GCs quickly reclaim short-lived objects in Young Gen; surviving objects are promoted to Old Gen where major GCs run.",
            "required_concepts": ["heap", "stack", "young generation", "old generation", "minor vs major gc"],
            "optional_concepts": ["eden", "survivor space", "metaspace", "g1gc regions", "stop-the-world"],
            "acceptable_alternatives": ["ZGC or Shenandoah low-latency concurrent region collectors"],
            "common_misconceptions": [
                "Thinking objects themselves live on the stack (only object references live on stack)",
                "Assuming calling System.gc() forces an immediate garbage collection"
            ],
            "rubric": {
                "heap_vs_stack_distinction": 35,
                "generational_hypothesis_explanation": 35,
                "promotion_and_gc_phases": 30
            },
            "follow_up_criteria": "Ask how Memory Leaks can happen in Java despite garbage collection.",
            "targetTime": "60-90 sec",
            "track": "Java Track"
        },
        {
            "id": 402,
            "question": "What is the difference between HashMap, HashTable, and ConcurrentHashMap in Java, and how does ConcurrentHashMap achieve thread safety without locking the entire map?",
            "topic": "Java Concurrency & Collections",
            "category": "Java Core & Concurrency",
            "difficulty": "Hard",
            "expected_answer": "HashMap is unsynchronized and permits null keys. HashTable synchronizes every method with a single table lock, causing high contention. ConcurrentHashMap uses lock striping and CAS (Compare-And-Swap) operations on individual hash buckets or tree bins, allowing concurrent reads without locking and isolated locks only per bucket on writes.",
            "reference_answer": "HashMap is unsynchronized and permits null keys. HashTable synchronizes every method with a single table lock, causing high contention. ConcurrentHashMap uses lock striping and CAS (Compare-And-Swap) operations on individual hash buckets or tree bins, allowing concurrent reads without locking and isolated locks only per bucket on writes.",
            "required_concepts": ["hashmap", "hashtable", "concurrenthashmap", "cas / compare-and-swap", "bucket lock / lock striping"],
            "optional_concepts": ["synchronized", "segment locking (java 7)", "tree bins (java 8)", "thread contention"],
            "acceptable_alternatives": ["Collections.synchronizedMap wrapper comparison"],
            "common_misconceptions": [
                "Believing ConcurrentHashMap locks the entire data structure during write operations",
                "Assuming HashMap is thread-safe for read-only operations when writers are concurrent"
            ],
            "rubric": {
                "comparison_of_three_collections": 35,
                "cas_and_bucket_level_locking": 40,
                "read_concurrency_without_locks": 25
            },
            "follow_up_criteria": "Ask how treeification (converting linked nodes to red-black trees) works in Java 8 HashMap.",
            "targetTime": "60-90 sec",
            "track": "Java Track"
        },
        {
            "id": 403,
            "question": "In Spring Boot, how does Dependency Injection and Inversion of Control (IoC) work, and what is the difference between Singleton and Prototype bean scopes?",
            "topic": "Spring Framework & Beans",
            "category": "Spring Boot Framework",
            "difficulty": "Medium",
            "expected_answer": "Spring IoC container manages object creation, configuration, and lifecycle via annotations like @Autowired, @Component, and @Service. Singleton scope (default) creates exactly one shared instance per Spring application context, while Prototype scope creates a new independent bean instance each time requested from the container.",
            "reference_answer": "Spring IoC container manages object creation, configuration, and lifecycle via annotations like @Autowired, @Component, and @Service. Singleton scope (default) creates exactly one shared instance per Spring application context, while Prototype scope creates a new independent bean instance each time requested from the container.",
            "required_concepts": ["ioc container", "dependency injection", "singleton scope", "prototype scope", "bean lifecycle"],
            "optional_concepts": ["applicationcontext", "request scope", "session scope", "@autowired", "@service"],
            "acceptable_alternatives": ["Constructor injection vs field injection discussion"],
            "common_misconceptions": [
                "Confusing Spring singleton scope (one per Spring context) with classic Gang of Four singleton (one per classloader)",
                "Assuming prototype beans have their destroy lifecycle managed by Spring (Spring does not manage destroy on prototype beans)"
            ],
            "rubric": {
                "ioc_concept_definition": 35,
                "singleton_scope_behavior": 35,
                "prototype_scope_behavior": 30
            },
            "follow_up_criteria": "Ask why constructor injection is preferred over field injection in Spring.",
            "targetTime": "45-90 sec",
            "track": "Spring Boot Track"
        }
    ],
    "spring": [
        {
            "id": 451,
            "question": "In Spring Boot, how does Dependency Injection and Inversion of Control (IoC) work, and what is the difference between Singleton and Prototype bean scopes?",
            "topic": "Spring Framework & Beans",
            "category": "Spring Boot Framework",
            "difficulty": "Medium",
            "expected_answer": "Spring IoC container manages object creation, configuration, and lifecycle via annotations like @Autowired, @Component, and @Service. Singleton scope (default) creates exactly one shared instance per Spring application context, while Prototype scope creates a new independent bean instance each time requested from the container.",
            "reference_answer": "Spring IoC container manages object creation, configuration, and lifecycle via annotations like @Autowired, @Component, and @Service. Singleton scope (default) creates exactly one shared instance per Spring application context, while Prototype scope creates a new independent bean instance each time requested from the container.",
            "required_concepts": ["ioc container", "dependency injection", "singleton scope", "prototype scope", "bean lifecycle"],
            "optional_concepts": ["applicationcontext", "request scope", "session scope", "@autowired", "@service"],
            "acceptable_alternatives": ["Constructor injection vs field injection discussion"],
            "common_misconceptions": [
                "Confusing Spring singleton scope with classic GoF singleton",
                "Assuming prototype beans have their destroy lifecycle managed by Spring"
            ],
            "rubric": {
                "ioc_concept_definition": 35,
                "singleton_scope_behavior": 35,
                "prototype_scope_behavior": 30
            },
            "follow_up_criteria": "Ask why constructor injection is preferred over field injection in Spring.",
            "targetTime": "45-90 sec",
            "track": "Spring Boot Track"
        }
    ],
    "csharp": [
        {
            "id": 501,
            "question": "In C# and .NET, how does async/await work under the hood using the Task-based Asynchronous Pattern and state machines?",
            "topic": "C# Asynchronous Programming",
            "category": "C# & .NET Core",
            "difficulty": "Hard",
            "expected_answer": "When the C# compiler compiles an async method, it transforms it into an IAsyncStateMachine struct. When awaiting an incomplete Task, execution yields control back to the caller while registering a continuation callback. When the task finishes, the thread pool or SynchronizationContext resumes execution at the next state without thread blocking.",
            "reference_answer": "When the C# compiler compiles an async method, it transforms it into an IAsyncStateMachine struct. When awaiting an incomplete Task, execution yields control back to the caller while registering a continuation callback. When the task finishes, the thread pool or SynchronizationContext resumes execution at the next state without thread blocking.",
            "required_concepts": ["state machine", "iasyncstatemachine", "continuation", "synchronizationcontext", "non-blocking"],
            "optional_concepts": ["task<t>", "valuetask", "configureawait(false)", "thread pool", "awaitable pattern"],
            "acceptable_alternatives": ["Mentioning ConfigureAwait(false) for avoiding context capture in library code"],
            "common_misconceptions": [
                "Thinking async creates a new background thread for each async method call",
                "Calling .Result or .Wait() on Tasks causing thread pool starvation or UI deadlocks"
            ],
            "rubric": {
                "compiler_state_machine_transformation": 40,
                "continuation_callback_mechanism": 35,
                "non_blocking_thread_resumption": 25
            },
            "follow_up_criteria": "Ask when to use ValueTask instead of Task.",
            "targetTime": "60-90 sec",
            "track": "C# & .NET Track"
        },
        {
            "id": 502,
            "question": "What is the difference between IEnumerable and IQueryable in C# LINQ, and how does query execution differ with Entity Framework Core?",
            "topic": "C# LINQ & Entity Framework Core",
            "category": "C# & LINQ Architecture",
            "difficulty": "Medium",
            "expected_answer": "IEnumerable operates in-memory using delegates (Func) with LINQ to Objects after records are fetched. IQueryable operates via Expression Trees, translating LINQ queries into SQL on the database server so only filtered and projected records are returned over the network.",
            "reference_answer": "IEnumerable operates in-memory using delegates (Func) with LINQ to Objects after records are fetched. IQueryable operates via Expression Trees, translating LINQ queries into SQL on the database server so only filtered and projected records are returned over the network.",
            "required_concepts": ["ienumerable", "iqueryable", "expression trees", "in-memory vs database", "sql translation"],
            "optional_concepts": ["deferred execution", "entity framework core", "func delegate", "network bandwidth"],
            "acceptable_alternatives": ["Discussing ToList() or AsEnumerable() as the materialization boundary"],
            "common_misconceptions": [
                "Filtering with IEnumerable on large database tables without realizing all rows are downloaded into memory first",
                "Assuming IQueryable executes immediately upon declaration"
            ],
            "rubric": {
                "in_memory_vs_server_side_execution": 40,
                "expression_trees_vs_delegates": 40,
                "ef_core_materialization_timing": 20
            },
            "follow_up_criteria": "Ask what causes client evaluation warnings in EF Core.",
            "targetTime": "45-90 sec",
            "track": "C# & .NET Track"
        }
    ],
    "php": [
        {
            "id": 601,
            "question": "In PHP 8+, how have modern features like OPcache preloading, typed properties, and attributes improved backend performance and reliability?",
            "topic": "Modern PHP 8+ Architecture",
            "category": "PHP Modern Architecture",
            "difficulty": "Medium",
            "expected_answer": "OPcache compiles PHP source into opcode in shared memory, and preloading compiles frameworks and classes on server startup so they are globally available without re-parsing per request. PHP 8 added strict typed properties, constructor property promotion, union types, and native attributes, enabling compile-time checks and type safety.",
            "reference_answer": "OPcache compiles PHP source into opcode in shared memory, and preloading compiles frameworks and classes on server startup so they are globally available without re-parsing per request. PHP 8 added strict typed properties, constructor property promotion, union types, and native attributes, enabling compile-time checks and type safety.",
            "required_concepts": ["opcache", "preloading", "typed properties", "attributes", "php 8 features"],
            "optional_concepts": ["jit compiler", "constructor property promotion", "match expression", "shared memory"],
            "acceptable_alternatives": ["Discussing PHP-FPM worker lifecycle optimizations"],
            "common_misconceptions": [
                "Believing PHP compiles ahead of time into a static binary executable",
                "Assuming OPcache preloaded files can be modified without restarting the PHP-FPM process"
            ],
            "rubric": {
                "opcache_preloading_mechanism": 40,
                "type_safety_and_attributes": 35,
                "performance_and_architecture_benefits": 25
            },
            "follow_up_criteria": "Ask how the PHP JIT compiler interacts with OPcache.",
            "targetTime": "45-90 sec",
            "track": "PHP Track"
        },
        {
            "id": 602,
            "question": "In Laravel, how does the Service Container handle dependency injection, and what is the difference between binding a singleton versus a transient binding?",
            "topic": "Laravel Framework Architecture",
            "category": "Laravel Architecture",
            "difficulty": "Medium",
            "expected_answer": "Laravel's Service Container uses PHP reflection to automatically resolve class dependencies declared in constructors and methods. A singleton binding resolves the class once and returns the exact same instance across the application lifecycle, while a transient/standard binding creates a fresh new instance every time.",
            "reference_answer": "Laravel's Service Container uses PHP reflection to automatically resolve class dependencies declared in constructors and methods. A singleton binding resolves the class once and returns the exact same instance across the application lifecycle, while a transient/standard binding creates a fresh new instance every time.",
            "required_concepts": ["service container", "dependency injection", "singleton binding", "transient / bind", "reflection"],
            "optional_concepts": ["service providers", "contracts", "facades", "app->make()"],
            "acceptable_alternatives": ["Scoped bindings in Laravel Octane"],
            "common_misconceptions": [
                "Assuming singletons persist between different HTTP requests in traditional PHP-FPM (they persist only for the single request)",
                "Thinking Facades bypass dependency injection completely"
            ],
            "rubric": {
                "service_container_reflection_explained": 35,
                "singleton_vs_transient_distinction": 40,
                "lifecycle_and_reusability": 25
            },
            "follow_up_criteria": "Ask how Laravel Octane changes the singleton lifecycle.",
            "targetTime": "45-90 sec",
            "track": "Laravel Track"
        }
    ],
    "javascript": [
        {
            "id": 700,
            "question": "Explain what a generator function is in JavaScript.",
            "topic": "JavaScript Iterators & Generators",
            "category": "Frontend & Web Development",
            "difficulty": "Medium",
            "expected_answer": "A generator function in JavaScript is defined with function* and uses the yield keyword to pause execution and produce values lazily. Calling a generator returns an iterator object with a next() method that yields an object with value and done properties. They are ideal for custom iterables, infinite streams, state machines, and handling asynchronous control flows.",
            "reference_answer": "A generator function in JavaScript is defined with function* and uses the yield keyword to pause execution and produce values lazily. Calling a generator returns an iterator object with a next() method that yields an object with value and done properties. They are ideal for custom iterables, infinite streams, state machines, and handling asynchronous control flows.",
            "required_concepts": ["function*", "yield", "iterator", "next()", "pause and resume execution"],
            "optional_concepts": ["lazy evaluation", "generator object", "value and done properties", "iterables"],
            "acceptable_alternatives": ["Explain generators in JS", "How do JavaScript generator functions work"],
            "misconceptions": [
                {"concept": "regular function execution", "correction": "Generator functions do not run immediately to completion; calling them returns an iterator that pauses at yield statements."}
            ]
        },
        {
            "id": 701,
            "question": "Explain the JavaScript Event Loop, the role of the Call Stack, Macro-task queue, and Micro-task queue, and in what order Promises and setTimeout execute.",
            "topic": "JavaScript Concurrency & Runtime",
            "category": "JavaScript Internals",
            "difficulty": "Hard",
            "expected_answer": "The JavaScript engine is single-threaded. Synchronous code executes on the Call Stack. When asynchronous operations resolve, micro-tasks (Promise callbacks, queueMicrotask) enter the Micro-task queue, while macro-tasks (setTimeout, setInterval, I/O) enter the Macro-task queue. The Event Loop prioritizes and drains the entire Micro-task queue before processing the next macro-task.",
            "reference_answer": "The JavaScript engine is single-threaded. Synchronous code executes on the Call Stack. When asynchronous operations resolve, micro-tasks (Promise callbacks, queueMicrotask) enter the Micro-task queue, while macro-tasks (setTimeout, setInterval, I/O) enter the Macro-task queue. The Event Loop prioritizes and drains the entire Micro-task queue before processing the next macro-task.",
            "required_concepts": ["call stack", "micro-task queue", "macro-task queue", "event loop", "promise priority over settimeout"],
            "optional_concepts": ["queueMicrotask", "single-threaded", "render queue", "requestAnimationFrame"],
            "acceptable_alternatives": ["Explaining execution sequence with a code snippet: sync -> microtask -> macrotask"],
            "common_misconceptions": [
                "Thinking setTimeout(fn, 0) runs immediately before resolved Promise callbacks",
                "Assuming asynchronous operations run in parallel JavaScript threads in the engine"
            ],
            "rubric": {
                "call_stack_and_single_thread_definition": 25,
                "microtask_vs_macrotask_distinction": 40,
                "execution_order_promises_first": 35
            },
            "follow_up_criteria": "Ask what happens if microtasks keep enqueuing more microtasks recursively (event loop starvation).",
            "targetTime": "60-90 sec",
            "track": "JavaScript Track"
        },
        {
            "id": 702,
            "question": "In React, how does the Virtual DOM reconciler (Fiber) optimize DOM updates, and what happens when you mutate state directly instead of using setState/useState setter?",
            "topic": "React Architecture & Reconciliation",
            "category": "React Architecture",
            "difficulty": "Hard",
            "expected_answer": "React Fiber represents components as an incremental virtual tree. It diffs virtual nodes using a heuristic reconciliation algorithm (comparing keys and types) and batches minimal real DOM mutations. Mutating state directly bypasses the state setter, failing to schedule a re-render and causing UI desynchronization bugs.",
            "reference_answer": "React Fiber represents components as an incremental virtual tree. It diffs virtual nodes using a heuristic reconciliation algorithm (comparing keys and types) and batches minimal real DOM mutations. Mutating state directly bypasses the state setter, failing to schedule a re-render and causing UI desynchronization bugs.",
            "required_concepts": ["virtual dom", "reconciliation / fiber", "diffing", "state immutability", "triggers re-render"],
            "optional_concepts": ["batching", "keys", "shallow equality", "commit phase", "render phase"],
            "acceptable_alternatives": ["Explaining concurrent features like startTransition and time-slicing in Fiber"],
            "common_misconceptions": [
                "Thinking React replaces the entire real DOM on every render",
                "Assuming direct mutation works if you force a re-render later (breaks memoization and concurrency)"
            ],
            "rubric": {
                "virtual_dom_diffing_explanation": 35,
                "why_direct_mutation_fails": 35,
                "batching_and_reconciliation_benefits": 30
            },
            "follow_up_criteria": "Ask how useMemo and useCallback prevent unnecessary component re-renders.",
            "targetTime": "60-90 sec",
            "track": "React Track"
        }
    ],
    "mysql": [
        {
            "id": 801,
            "question": "How do B-Tree indexes work in MySQL InnoDB, and why can queries with leading wildcards (e.g. LIKE '%abc') not use index seek operations?",
            "topic": "MySQL Indexing & Storage Engine",
            "category": "MySQL & Database Engineering",
            "difficulty": "Hard",
            "expected_answer": "InnoDB indexes organize keys in a balanced B+Tree where data is sorted lexicographically. Searches navigate from root to leaf using prefix matching. A leading wildcard removes the left prefix, making it impossible to navigate the sorted tree and forcing a full index scan or table scan.",
            "reference_answer": "InnoDB indexes organize keys in a balanced B+Tree where data is sorted lexicographically. Searches navigate from root to leaf using prefix matching. A leading wildcard removes the left prefix, making it impossible to navigate the sorted tree and forcing a full index scan or table scan.",
            "required_concepts": ["b-tree / b+tree", "lexicographical sort", "prefix matching", "leading wildcard", "index scan vs index seek"],
            "optional_concepts": ["clustered index", "leaf nodes", "full table scan", "composite index left-prefix rule"],
            "acceptable_alternatives": ["Suggesting Full-Text Indexing (FULLTEXT) or Elasticsearch for substring search"],
            "common_misconceptions": [
                "Thinking any index column automatically accelerates any WHERE clause regardless of wildcard position",
                "Assuming trailing wildcards (LIKE 'abc%') also fail to use indexes (trailing wildcards DO use indexes)"
            ],
            "rubric": {
                "b_plus_tree_sorted_order_explained": 35,
                "left_prefix_rule_explanation": 35,
                "consequence_full_scan_vs_seek": 30
            },
            "follow_up_criteria": "Ask how composite indexes (colA, colB) handle queries filtering only on colB.",
            "targetTime": "60-90 sec",
            "track": "Database Track"
        },
        {
            "id": 802,
            "question": "Explain the four ACID properties in relational database transactions, and how MySQL implements isolation levels like Read Committed versus Repeatable Read.",
            "topic": "Database ACID & Transaction Isolation",
            "category": "Database Systems",
            "difficulty": "Medium",
            "expected_answer": "ACID stands for Atomicity, Consistency, Isolation, and Durability. InnoDB implements transaction isolation using Multi-Version Concurrency Control (MVCC) and undo logs. Read Committed reads the latest committed snapshot for each statement, while Repeatable Read maintains a consistent read snapshot established at the start of the transaction.",
            "reference_answer": "ACID stands for Atomicity, Consistency, Isolation, and Durability. InnoDB implements transaction isolation using Multi-Version Concurrency Control (MVCC) and undo logs. Read Committed reads the latest committed snapshot for each statement, while Repeatable Read maintains a consistent read snapshot established at the start of the transaction.",
            "required_concepts": ["atomicity", "consistency", "isolation", "durability", "mvcc", "repeatable read vs read committed"],
            "optional_concepts": ["undo logs", "redo log / write-ahead log", "phantom reads", "dirty reads", "snapshot isolation"],
            "acceptable_alternatives": ["Explaining lock-based isolation via two-phase locking (2PL)"],
            "common_misconceptions": [
                "Assuming Repeatable Read prevents all phantom reads without gap locking",
                "Confusing Durability with in-memory caching"
            ],
            "rubric": {
                "acid_definitions": 30,
                "mvcc_and_undo_logs": 35,
                "read_committed_vs_repeatable_read": 35
            },
            "follow_up_criteria": "Ask what a dirty read is and which isolation level prevents it.",
            "targetTime": "60-90 sec",
            "track": "Database Track"
        }
    ],
    "oracle": [
        {
            "id": 851,
            "question": "In Oracle Database, how does Multi-Version Concurrency Control (MVCC) and the Undo tablespace ensure statement-level read consistency without locking tables?",
            "topic": "Oracle MVCC & Undo Architecture",
            "category": "Oracle Database Architecture",
            "difficulty": "Hard",
            "expected_answer": "Oracle guarantees readers do not block writers and writers do not block readers. When a query begins, Oracle notes the System Commit Number (SCN). If another transaction modifies and commits data while the query is running, Oracle reconstructs before-images from the Undo tablespace to present a consistent snapshot as of the query's start SCN.",
            "reference_answer": "Oracle guarantees readers do not block writers and writers do not block readers. When a query begins, Oracle notes the System Commit Number (SCN). If another transaction modifies and commits data while the query is running, Oracle reconstructs before-images from the Undo tablespace to present a consistent snapshot as of the query's start SCN.",
            "required_concepts": ["system commit number / scn", "undo tablespace", "mvcc", "read consistency", "non-blocking readers/writers"],
            "optional_concepts": ["snapshot too old (ora-01555)", "before-images", "rollback segment", "consistent read"],
            "acceptable_alternatives": ["Discussing Flashback Query using SCN or timestamp"],
            "common_misconceptions": [
                "Thinking Oracle places shared read locks on tables during SELECT queries",
                "Assuming undo data is stored in temporary tablespaces"
            ],
            "rubric": {
                "scn_snapshot_explanation": 40,
                "undo_tablespace_before_image_reconstruction": 40,
                "concurrency_without_locking": 20
            },
            "follow_up_criteria": "Ask what causes ORA-01555 (snapshot too old) and how to mitigate it.",
            "targetTime": "60-90 sec",
            "track": "Oracle Track"
        }
    ],
    "cybersecurity": [
        {
            "id": 901,
            "question": "What is SQL Injection, how does it occur at the protocol and parser level, and why do parameterized queries (prepared statements) provide foolproof prevention?",
            "topic": "Application Security & Injection Prevention",
            "category": "Cybersecurity & OWASP",
            "difficulty": "Medium",
            "expected_answer": "SQL Injection occurs when untrusted user input is directly concatenated into a dynamic SQL string, allowing input to alter the SQL syntax and query execution plan. Parameterized queries compile the SQL statement structure first, treating user input strictly as literal values or parameters that cannot alter SQL grammar regardless of characters provided.",
            "reference_answer": "SQL Injection occurs when untrusted user input is directly concatenated into a dynamic SQL string, allowing input to alter the SQL syntax and query execution plan. Parameterized queries compile the SQL statement structure first, treating user input strictly as literal values or parameters that cannot alter SQL grammar regardless of characters provided.",
            "required_concepts": ["sql injection", "string concatenation", "prepared statements / parameterized queries", "syntax vs data separation", "query compilation"],
            "optional_concepts": ["orm protection", "input sanitization", "least privilege", "owasp top 10", "escaping"],
            "acceptable_alternatives": ["Discussing stored procedures with parameter bindings"],
            "common_misconceptions": [
                "Thinking simple regex input filtering or string escaping is safer than parameterized queries",
                "Assuming ORMs are automatically immune to SQL injection if raw queries are used"
            ],
            "rubric": {
                "root_cause_concatenation_explained": 35,
                "parameterized_queries_mechanism": 45,
                "limitations_of_regex_filtering": 20
            },
            "follow_up_criteria": "Ask how to handle dynamic table names or column names safely since they cannot be parameterized.",
            "targetTime": "60-90 sec",
            "track": "Cybersecurity Track"
        },
        {
            "id": 902,
            "question": "Explain the difference between Symmetric and Asymmetric Encryption, and how both are combined in TLS/HTTPS to provide secure, high-performance communication.",
            "topic": "Cryptography & Network Security",
            "category": "Cybersecurity & Cryptography",
            "difficulty": "Hard",
            "expected_answer": "Symmetric encryption uses a single shared secret key for encryption and decryption, offering high computational speed (e.g. AES). Asymmetric encryption uses a public-private key pair (e.g. RSA, ECC), enabling secure key exchange and authentication without prior shared secrets. In TLS/HTTPS, asymmetric encryption is used during the TLS handshake to authenticate the server and exchange a session key, which is then used with symmetric encryption to encrypt data traffic at high speed.",
            "reference_answer": "Symmetric encryption uses a single shared secret key for encryption and decryption, offering high computational speed (e.g. AES). Asymmetric encryption uses a public-private key pair (e.g. RSA, ECC), enabling secure key exchange and authentication without prior shared secrets. In TLS/HTTPS, asymmetric encryption is used during the TLS handshake to authenticate the server and exchange a session key, which is then used with symmetric encryption to encrypt data traffic at high speed.",
            "required_concepts": ["symmetric encryption", "asymmetric encryption", "single key vs key pair", "tls/https handshake", "session key"],
            "optional_concepts": ["aes", "rsa", "elliptic curve", "diffie-hellman", "certificate authority", "forward secrecy"],
            "acceptable_alternatives": ["Diffie-Hellman key exchange explanation for ephemeral keys"],
            "common_misconceptions": [
                "Thinking entire HTTPS payloads are encrypted with asymmetric keys (that would be computationally too slow)",
                "Assuming public keys can decrypt messages encrypted with the same public key"
            ],
            "rubric": {
                "symmetric_vs_asymmetric_distinction": 35,
                "hybrid_encryption_in_tls": 45,
                "speed_and_security_tradeoff": 20
            },
            "follow_up_criteria": "Ask what Perfect Forward Secrecy (PFS) is in modern TLS.",
            "targetTime": "60-90 sec",
            "track": "Cybersecurity Track"
        }
    ],
    "ai_ml": [
        {
            "id": 1001,
            "question": "What is the difference between Overfitting and Underfitting in Machine Learning, and how do regularization techniques (L1 Lasso and L2 Ridge) mitigate overfitting?",
            "topic": "Machine Learning Fundamentals & Regularization",
            "category": "AI/ML Engineering",
            "difficulty": "Medium",
            "expected_answer": "Underfitting occurs when a model is too simple to capture patterns, causing high bias and poor training and test accuracy. Overfitting occurs when a model memorizes noise in training data, causing high variance and poor generalization. L1 regularization (Lasso) adds absolute weight penalties, driving coefficients to zero for feature selection. L2 regularization (Ridge) adds squared weight penalties, shrinking weights to prevent large dominant coefficients.",
            "reference_answer": "Underfitting occurs when a model is too simple to capture patterns, causing high bias and poor training and test accuracy. Overfitting occurs when a model memorizes noise in training data, causing high variance and poor generalization. L1 regularization (Lasso) adds absolute weight penalties, driving coefficients to zero for feature selection. L2 regularization (Ridge) adds squared weight penalties, shrinking weights to prevent large dominant coefficients.",
            "required_concepts": ["overfitting", "underfitting", "bias-variance tradeoff", "l1 / lasso", "l2 / ridge"],
            "optional_concepts": ["weight shrinkage", "sparsity", "cross-validation", "dropout", "early stopping"],
            "acceptable_alternatives": ["Discussing dropout or early stopping in deep neural networks"],
            "common_misconceptions": [
                "Thinking higher training accuracy always implies a better real-world model",
                "Confusing L1 (sparse coefficients) with L2 (smooth shrinkage)"
            ],
            "rubric": {
                "bias_variance_definitions": 35,
                "l1_lasso_sparse_shrinkage": 35,
                "l2_ridge_weight_penalty": 30
            },
            "follow_up_criteria": "Ask how ElasticNet combines both L1 and L2 penalties.",
            "targetTime": "60-90 sec",
            "track": "AI/ML Track"
        }
    ],
    "system_design": [
        {
            "id": 1101,
            "question": "How would you design a distributed rate limiter for a high-traffic backend API? What are the trade-offs between Token Bucket, Leaky Bucket, and Sliding Window algorithms?",
            "topic": "Distributed System Design & Throttling",
            "category": "System Design",
            "difficulty": "Hard",
            "expected_answer": "A distributed rate limiter uses Redis with atomic Lua scripts. Token Bucket allows bursts up to bucket capacity and refills steadily; Leaky Bucket outputs at a steady constant rate; Sliding Window log or counter tracks requests within dynamic timestamps, providing smooth throttling without burst boundary spikes.",
            "reference_answer": "A distributed rate limiter uses Redis with atomic Lua scripts. Token Bucket allows bursts up to bucket capacity and refills steadily; Leaky Bucket outputs at a steady constant rate; Sliding Window log or counter tracks requests within dynamic timestamps, providing smooth throttling without burst boundary spikes.",
            "required_concepts": ["rate limiting", "token bucket", "leaky bucket", "sliding window", "redis / distributed atomic counter"],
            "optional_concepts": ["lua script", "concurrency race conditions", "burst allowance", "429 too many requests"],
            "acceptable_alternatives": ["Sliding window counter with sub-bucket hashing"],
            "common_misconceptions": [
                "Using non-atomic GET then INCR operations in Redis leading to race conditions",
                "Assuming fixed window counters prevent boundary traffic spikes"
            ],
            "rubric": {
                "algorithm_tradeoffs_explained": 40,
                "distributed_coordination_redis_lua": 40,
                "boundary_condition_handling": 20
            },
            "follow_up_criteria": "Ask how to handle rate limiting when Redis experiences a failover or network partition.",
            "targetTime": "60-120 sec",
            "track": "System Design Track"
        }
    ],
    "behavioral": [
        {
            "id": 1201,
            "question": "Describe a challenging technical disagreement you had with a team member regarding architecture or system design. How did you evaluate both perspectives and reach consensus?",
            "topic": "Technical Collaboration & STAR Method",
            "category": "Behavioral & STAR",
            "difficulty": "Medium",
            "expected_answer": "An effective response follows the STAR method: describes the specific technical conflict objectively, emphasizes data-driven evaluation (prototyping, benchmarking latency, evaluating long-term maintenance costs), active listening, and committing to the best solution for the product.",
            "reference_answer": "An effective response follows the STAR method: describes the specific technical conflict objectively, emphasizes data-driven evaluation (prototyping, benchmarking latency, evaluating long-term maintenance costs), active listening, and committing to the best solution for the product.",
            "required_concepts": ["situation", "task", "action", "result", "data-driven evaluation"],
            "optional_concepts": ["benchmarking", "compromise", "active listening", "blameless communication", "post-mortem"],
            "acceptable_alternatives": ["Discussing RFC documents and team architectural reviews"],
            "common_misconceptions": [
                "Focusing on interpersonal blame rather than the technical merits and trade-offs",
                "Omitting measurable outcomes or lessons learned"
            ],
            "rubric": {
                "star_framework_adherence": 35,
                "objective_data_driven_action": 35,
                "clear_measurable_result": 30
            },
            "follow_up_criteria": "Ask what they would do differently if faced with the same scenario today.",
            "targetTime": "60-90 sec",
            "track": "Behavioral & STAR"
        }
    ]
}


def synthesize_project_question(project: Dict[str, Any], role: str, target_diff: str, q_index: int) -> Dict[str, Any]:
    """
    Synthesizes a deep-dive technical question with complete evaluation rubric
    tailored specifically to the candidate's actual resume project.
    """
    title = project.get("title") or project.get("name") or "your featured technical project"
    tech_summary = project.get("tech_summary") or ", ".join(project.get("technologies", [])[:4]) or "the chosen tech stack"
    desc = project.get("description") or ""

    if q_index == 1:
        question = (
            f"In your project '{title}' built with {tech_summary}, what architectural decisions did you make "
            f"during implementation, how did you structure the components and data flow, and what was "
            f"the most critical technical challenge you overcame?"
        )
        expected_answer = (
            f"In {title}, architecting with {tech_summary} requires defining modular service boundaries, "
            f"clean API contracts, and robust error handling. The critical challenge involved balancing implementation "
            f"trade-offs, optimizing data pipelines, and ensuring test coverage across edge cases."
        )
        required_concepts = ["architectural decisions", "component structure", "data flow", "technical challenge", "solution trade-offs"]
        optional_concepts = ["api contracts", "state management", "error handling", "performance bottlenecks"]
        category = "Project Architecture"
    elif q_index == 2:
        question = (
            f"For your project '{title}', walk me through how you handled data persistence, query optimization, "
            f"and error resilience with {tech_summary}. How did you verify that the application performed reliably?"
        )
        expected_answer = (
            f"In {title}, data persistence requires structured schema design, transaction atomicity, and indexing on "
            f"frequently queried fields. Concurrency and resilience are verified using automated unit/integration tests, "
            f"logging, exception handling, and connection pooling."
        )
        required_concepts = ["data persistence", "query optimization", "error resilience", "testing/verification", "indexing or pooling"]
        optional_concepts = ["transactions", "caching", "mocking", "monitoring", "latency"]
        category = "Project Implementation"
    else:
        question = (
            f"Regarding your work on '{title}' ({tech_summary}), what technical trade-off would you reconsider if you were to refactor "
            f"it for high scalability today, and how would you enhance its security and performance?"
        )
        expected_answer = (
            f"Refactoring {title} for higher scale involves introducing asynchronous background processing or caching, "
            f"addressing database bottlenecks, enforcing strict authentication/authorization checks, and establishing CI/CD automation."
        )
        required_concepts = ["trade-off", "refactoring", "scalability", "security", "performance"]
        optional_concepts = ["caching", "async workers", "rate limiting", "load balancing"]
        category = "Project Refactoring"

    return {
        "id": 9000 + q_index,
        "question": question,
        "expected_answer": expected_answer,
        "reference_answer": expected_answer,
        "category": category,
        "topic": f"Project Deep Dive: {title[:30]}",
        "difficulty": target_diff,
        "required_concepts": required_concepts,
        "optional_concepts": optional_concepts,
        "acceptable_alternatives": ["Accept valid technical alternatives implemented by candidate for their specific application domain."],
        "common_misconceptions": [
            "Giving vague buzzwords without specific architectural context from the project",
            "Claiming zero trade-offs or challenges existed"
        ],
        "rubric": {
            "architectural_clarity": 35,
            "technical_depth_and_tradeoffs": 40,
            "concrete_implementation_details": 25
        },
        "follow_up_criteria": "Ask for specific metrics, database schemas, or API status codes used in the project.",
        "targetTime": "60-120 sec",
        "track": f"Project - {title[:20]}"
    }


def normalize_question_tokens(text: str) -> Set[str]:
    """Extract normalized word tokens for duplicate detection."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stop = {"what", "how", "why", "difference", "between", "explain", "describe", "in", "the", "and", "your", "does"}
    return set(w for w in words if w not in stop)


def is_duplicate_question(new_q_text: str, existing_questions: List[Any]) -> bool:
    """Checks if new question is a duplicate or superficial rewording."""
    new_tokens = normalize_question_tokens(new_q_text)
    if not new_tokens:
        return False

    for eq in existing_questions:
        eq_text = eq.get("question", "") if isinstance(eq, dict) else str(eq)
        eq_tokens = normalize_question_tokens(eq_text)
        if not eq_tokens:
            continue
        intersection = len(new_tokens & eq_tokens)
        min_len = min(len(new_tokens), len(eq_tokens))
        if min_len > 0 and (intersection / min_len) >= 0.70:
            return True
    return False


def get_academic_questions_from_db(
    db: Optional[Any] = None,
    count: int = 5,
    role: Optional[str] = None,
    difficulty: Optional[str] = None,
    skills: Optional[Any] = None,
    profile_data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves verified technical interview questions strictly from active academic_train records in MySQL.
    Strictly adheres to Part B Step 3 constraints:
    - Only active academic_train records are eligible (academic_val, academic_test, curated_seed are quarantined).
    - Never generates new questions or calls LLMs/external APIs.
    - Zero random question generation or hardcoded fallback question arrays.
    - Preserves internal traceability to source_dataset and source_id.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        count = max(1, min(int(count or 5), 20))
        
        # Collect keywords for domain-specific matching
        keywords = []
        if skills:
            if isinstance(skills, str):
                keywords.extend([s.strip().lower() for s in skills.split(",") if s.strip()])
            elif isinstance(skills, list):
                keywords.extend([str(s).strip().lower() for s in skills if s])

        if role and isinstance(role, str):
            for word in role.split():
                if len(word) > 3 and word.lower() not in ["developer", "engineer", "software", "senior", "junior"]:
                    keywords.append(word.lower())

        if profile_data:
            parsed = profile_data.get("parsed_resume") or {}
            c_skills = profile_data.get("skills") or parsed.get("skills") or []
            if isinstance(c_skills, str):
                keywords.extend([s.strip().lower() for s in c_skills.split(",") if s.strip()])
            elif isinstance(c_skills, list):
                keywords.extend([str(s).strip().lower() for s in c_skills if s])

            p_role = profile_data.get("target_role")
            if p_role and isinstance(p_role, str):
                for word in p_role.split():
                    if len(word) > 3 and word.lower() not in ["developer", "engineer", "software", "senior", "junior"]:
                        keywords.append(word.lower())

        keywords = list(dict.fromkeys(keywords))  # deduplicate preserving order

        # Strict query: ONLY active academic_train records!
        base_query = db.query(models.Question).filter(
            models.Question.is_active == 1,
            models.Question.source_dataset == "academic_train"
        )

        selected = []
        selected_ids = set()

        diff_filter = None
        if difficulty and difficulty.strip() and difficulty.strip().lower() in ["easy", "medium", "hard"]:
            diff_filter = models.Question.difficulty == difficulty.strip().capitalize()

        # Step 1: If domain keywords are present (from profile / resume skills), match them first
        if keywords:
            conditions = [models.Question.question_text.ilike(f"%{kw}%") for kw in keywords if len(kw) >= 2]
            if conditions:
                stage1_base = base_query.filter(diff_filter) if diff_filter is not None else base_query
                matched = stage1_base.filter(or_(*conditions)).order_by(models.Question.id.asc()).limit(count).all()
                for q in matched:
                    if q.id not in selected_ids:
                        selected.append(q)
                        selected_ids.add(q.id)

        # Step 2: If more questions needed, match by target role and difficulty
        if len(selected) < count and (role or difficulty):
            rem = count - len(selected)
            stage_query = base_query
            if selected_ids:
                stage_query = stage_query.filter(~models.Question.id.in_(selected_ids))

            filters = []
            if role and role.strip() and role.strip() != "Other":
                filters.append(models.Question.role.ilike(f"%{role.strip()}%"))
            if diff_filter is not None:
                filters.append(diff_filter)

            if filters:
                matched_role_diff = stage_query.filter(*filters).order_by(models.Question.id.asc()).limit(rem).all()
                for q in matched_role_diff:
                    if q.id not in selected_ids:
                        selected.append(q)
                        selected_ids.add(q.id)

        # Step 3: If still needed and role filter provided, match role alone
        if len(selected) < count and role and role.strip() and role.strip() != "Other":
            rem = count - len(selected)
            stage_query = base_query.filter(models.Question.role.ilike(f"%{role.strip()}%"))
            if selected_ids:
                stage_query = stage_query.filter(~models.Question.id.in_(selected_ids))
            for q in stage_query.order_by(models.Question.id.asc()).limit(rem).all():
                if q.id not in selected_ids:
                    selected.append(q)
                    selected_ids.add(q.id)

        # Step 4: Fill remaining slots from active academic_train pool
        if len(selected) < count:
            remaining = count - len(selected)
            filler_query = base_query
            if selected_ids:
                filler_query = filler_query.filter(~models.Question.id.in_(selected_ids))
            fillers = filler_query.order_by(models.Question.id.asc()).limit(remaining).all()
            for q in fillers:
                if q.id not in selected_ids:
                    selected.append(q)
                    selected_ids.add(q.id)

        result_deck = []
        for q in selected:
            concepts = extract_key_concepts(q.reference_answer)
            eval_spec = {
                "expected_answer": q.reference_answer,
                "required_concepts": concepts[:5] if concepts else ["technical explanation", "correct principles"],
                "optional_concepts": concepts[5:10] if len(concepts) > 5 else [],
                "acceptable_alternatives": [],
                "common_misconceptions": [],
                "rubric": {"accuracy": 60, "clarity": 40}
            }

            result_deck.append({
                "id": q.id,
                "question": q.question_text,
                "question_text": q.question_text,
                "source_id": q.source_id,
                "category": q.category or "Academic Technical",
                "difficulty": q.difficulty or difficulty or "Medium",
                "role": q.role or role or "Software Engineer",
                "skill": q.skill or (keywords[0] if keywords else None),
                "source_dataset": q.source_dataset,
                "reference_answer": q.reference_answer,
                "evaluation_spec": eval_spec
            })

        return result_deck
    finally:
        if close_db:
            db.close()


def generate_personalized_questions(
    profile_data: Optional[Dict[str, Any]] = None,
    num_questions: int = 5,
    difficulty: Optional[str] = None,
    role: Optional[str] = None,
    experience_level: Optional[str] = None,
    interview_type: Optional[str] = None,
    db: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves candidate-specific technical interview deck from active academic_train database records.
    Aligns questions with actual skills, projects, and target role.
    Strictly prohibits LLM generation, random question generation, or hardcoded arrays.
    """
    if not profile_data:
        profile_data = {}

    target_role = role or profile_data.get("target_role") or "Software Engineer"
    target_diff = difficulty or profile_data.get("interview_difficulty") or "Medium"

    return get_academic_questions_from_db(
        db=db,
        count=num_questions,
        role=target_role,
        difficulty=target_diff,
        profile_data=profile_data
    )


def get_interview_questions(db: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Returns verified academic interview questions from MySQL database."""
    return get_academic_questions_from_db(db=db, count=5)
