'use strict';

// Hexo 3's generator clears its cache stream in destroy(). Modern Node.js
// auto-destroys Transform streams when they finish, so generated files become
// empty before Hexo writes the cached content.
const stream = require('stream');
const OriginalTransform = stream.Transform;

function LegacyTransform(options) {
  if (!(this instanceof LegacyTransform)) return new LegacyTransform(options);

  OriginalTransform.call(this, Object.assign({}, options, {
    autoDestroy: false
  }));
}

LegacyTransform.prototype = OriginalTransform.prototype;
stream.Transform = LegacyTransform;

require('hexo-cli')().then(
  () => process.exit(0),
  () => process.exit(1)
);
