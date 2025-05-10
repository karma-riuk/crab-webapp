/*
 * Calculates BLEU score between a reference and candidate sentence.
 * Reference and candidate should be token arrays (e.g. split by whitespace).
 * We compute modified n-gram precisions for n=1..4, geometric mean, with smoothing (optional).
 * We include the brevity penalty.
 */

/**
 * Extracts n-grams from a sequence of tokens.
 * @param {string[]} tokens - Array of tokens.
 * @param {number} n - Size of the n-gram.
 * @returns {Object} Map from n-gram string to its count.
 */
function getNGramCounts(tokens, n) {
    const counts = Object.create(null);
    for (let i = 0; i + n <= tokens.length; i++) {
        const gram = tokens.slice(i, i + n).join(" ");
        counts[gram] = (counts[gram] || 0) + 1;
    }
    return counts;
}

/**
 * Computes modified precision for a given n.
 * @param {string[]} reference - Reference token array.
 * @param {string[]} candidate - Candidate token array.
 * @param {number} n - n-gram order.
 * @returns {number} Modified n-gram precision.
 */
function modifiedPrecision(reference, candidate, n) {
    const refCounts = getNGramCounts(reference, n);
    const candCounts = getNGramCounts(candidate, n);
    let matchCount = 0;
    let totalCount = 0;

    for (const gram in candCounts) {
        const countCand = candCounts[gram];
        const countRef = refCounts[gram] || 0;
        matchCount += Math.min(countCand, countRef);
        totalCount += countCand;
    }

    // Avoid division by zero
    return totalCount === 0 ? 0 : matchCount / totalCount;
}

/**
 * Computes brevity penalty.
 * @param {number} refLength - Length of reference sentence.
 * @param {number} candLength - Length of candidate sentence.
 * @returns {number} Brevity penalty.
 */
function brevityPenalty(refLength, candLength) {
    if (candLength > refLength) {
        return 1;
    }
    if (candLength === 0) {
        return 0;
    }
    return Math.exp(1 - refLength / candLength);
}

/**
 * Computes BLEU score.
 * @param {string} refSentence - Reference sentence.
 * @param {string} candSentence - Candidate sentence.
 * @param {number} maxN - Maximum n-gram order (default=4).
 * @param {boolean} smooth - Whether to apply smoothing (default=false).
 * @returns {number} BLEU score between 0 and 1.
 */
export function bleu(refSentence, candSentence, maxN = 4, smooth = false) {
    const reference = refSentence.trim().split(/\s+/);
    const candidate = candSentence.trim().split(/\s+/);
    const refLen = reference.length;
    const candLen = candidate.length;

    // count how many times we've hit a zero count so far
    const precisions = [];
    for (let n = 1; n <= maxN; n++) {
        let p = modifiedPrecision(reference, candidate, n);
        if (p === 0 && smooth) {
            p = 1 / Math.pow(candLen, n);
        }
        precisions.push(p);
    }

    // Compute geometric mean of precisions
    // if any precision is zero (and no smoothing), BLEU=0
    if (precisions.some((p) => p === 0)) {
        return 0;
    }

    const logPrecisionSum =
        precisions.map((p) => Math.log(p)).reduce((a, b) => a + b, 0) / maxN;
    const geoMean = Math.exp(logPrecisionSum);

    const bp = brevityPenalty(refLen, candLen);
    return bp * geoMean;
}

// Example usage:

if (process.argv[1] === import.meta.filename) {
    const test_pairs = [
        // ["the cat is on the mat", "the cat is on the mat"],
        // ["the cat is on the mat", "the the the the the the the"],
        // ["the cat is on the mat", "the cat on the mat"],
        // ["the cat is on the mat", "the cat is on the"],
        // ["the cat is on the mat", "foo bar baz qux"],
        // [
        //     "The quick brown fox jumps over the lazy dog",
        //     "The quick brown dog jumps over the lazy fox",
        // ],
        [
            "This could be `static` to prevent any funkiness, i.e. attempting to use class state during the constructor or similar.",
            "This could be `static` to prevent any funkiness, i.e. attempting to use class state during the constructor or similar.",
        ],
    ];

    for (const [reference, candidate] of test_pairs) {
        const score = bleu(reference, candidate, 4);
        console.log(`reference: ${reference}`);
        console.log(`candidate: ${candidate}`);
        console.log(`BLEU score: ${score.toFixed(4)}`);
    }
}
