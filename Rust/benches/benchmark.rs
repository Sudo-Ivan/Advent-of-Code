use criterion::{criterion_group, criterion_main, Criterion};
use aoc_benchmark_rust::day1;

pub fn benchmark_day1(c: &mut Criterion) {
    let input = vec![/* your test input */];
    c.bench_function("day1", |b| b.iter(|| day1::count_increases(&input)));
}

criterion_group!(benches, benchmark_day1);
criterion_main!(benches);