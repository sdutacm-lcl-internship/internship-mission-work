const processData = (user) => {
    let result = {};
    if ('rating' in user) {
        result = {
            handle: user.handle,
            rating: user.rating,
            rank: user.rank
        };
    } else {
        result = {
            handle: user.handle,
        };
    }
    return result;
};

export default processData;