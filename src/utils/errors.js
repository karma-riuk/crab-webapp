export class InvalidJsonFormatError extends Error {
    constructor(message = 'JSON must be an object mapping strings to strings') {
        super(message);
        this.name = 'InvalidJsonFormatError';
    }
} 