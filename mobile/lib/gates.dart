/// Dart port of decisiongate/gates.py heuristics (v0.1). Sequential.
/// First non-PASS stops the chain. Not predictive, advisory, or prescriptive.

const pass = 'PASS';
const revise = 'REVISE';
const block = 'BLOCK';

const motto =
    'Freedom without clarity is chaos. Clarity without force is wisdom.';

const hedges = {'maybe', 'somehow', 'stuff', 'things'};

const commonVerbs = {
  'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am',
  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
  'shall', 'should', 'can', 'could', 'must', 'need', 'needs',
  'make', 'makes', 'made', 'take', 'takes', 'took', 'give',
  'gives', 'gave', 'go', 'goes', 'went', 'come', 'keep', 'put',
  'use', 'uses', 'used', 'set', 'get', 'let', 'allow', 'allows',
  'publish', 'release', 'releases', 'deploy', 'ship', 'open',
  'close', 'create', 'created', 'delete', 'write', 'read', 'run',
  'execute', 'adopt', 'reject', 'approve', 'block', 'collect',
  'store', 'share', 'send', 'build', 'launch', 'hire', 'spend',
  'buy', 'sell', 'migrate', 'replace', 'update', 'install',
  'announce', 'commit', 'sign', 'fund', 'grant', 'revoke',
  'host', 'serve', 'bind', 'filter', 'record', 'name', 'assign',
  'document', 'provide', 'provides', 'include', 'includes',
  'add', 'remove', 'stop', 'start', 'move', 'change', 'apply',
  'submit', 'accept', 'refuse', 'pay', 'offer', 'request',
  'require', 'requires', 'implement', 'implements',
};

const negationMarkers = [
  'do not ',
  "don't ",
  'does not ',
  "doesn't ",
  'must not ',
  'cannot ',
  "can't ",
  'never ',
  'no ',
  'not ',
  'without ',
];

class Proposal {
  Proposal({
    this.statement = '',
    this.evidence = const [],
    this.impactsPositive = const [],
    this.impactsNegative = const [],
    this.values = const [],
    this.constraints = const [],
    this.accountablePerson = '',
  });

  final String statement;
  final List<String> evidence;
  final List<String> impactsPositive;
  final List<String> impactsNegative;
  final List<String> values;
  final List<String> constraints;
  final String accountablePerson;

  List<String> _lines(List<String> xs) =>
      xs.map((e) => e.trim()).where((e) => e.isNotEmpty).toList();

  Proposal normalized() => Proposal(
        statement: statement.trim(),
        evidence: _lines(evidence),
        impactsPositive: _lines(impactsPositive),
        impactsNegative: _lines(impactsNegative),
        values: _lines(values),
        constraints: _lines(constraints),
        accountablePerson: accountablePerson.trim(),
      );
}

class GateResult {
  GateResult({
    required this.name,
    required this.state,
    required this.feedback,
  });
  final String name;
  final String state;
  final String feedback;
}

class Report {
  Report({
    required this.lineage,
    required this.finalState,
    this.blockedAt,
  });
  final List<GateResult> lineage;
  final String finalState;
  final String? blockedAt;
}

final _wordRe = RegExp(r'[A-Za-z0-9][A-Za-z0-9._+-]*');

List<String> tokenize(String text) =>
    _wordRe.allMatches(text.toLowerCase()).map((m) => m.group(0)!).toList();

bool _looksLikeVerb(String token) {
  if (commonVerbs.contains(token)) return true;
  if (token.length > 4 &&
      (token.endsWith('ing') ||
          token.endsWith('ize') ||
          token.endsWith('ise') ||
          token.endsWith('ify'))) {
    return true;
  }
  if (token.length > 4 && token.endsWith('ed')) return true;
  return false;
}

bool hasVerbAndObject(List<String> tokens) {
  final content = tokens.where((t) => !hedges.contains(t)).toList();
  if (content.length < 2) return false;
  return content.any(_looksLikeVerb);
}

GateResult gateDefinition(Proposal p) {
  final statement = p.statement.trim();
  if (statement.isEmpty) {
    return GateResult(
      name: 'Definition',
      state: block,
      feedback:
          'Statement is empty. A proposal with no concrete statement cannot '
          'pass Definition. Write an unambiguous action with a verb and an '
          'object, at least 12 words.',
    );
  }
  final tokens = tokenize(statement);
  if (tokens.length < 12) {
    return GateResult(
      name: 'Definition',
      state: revise,
      feedback:
          'Statement has ${tokens.length} word(s); Definition requires at '
          'least 12. Expand into a concrete, unambiguous proposal.',
    );
  }
  if (!hasVerbAndObject(tokens)) {
    return GateResult(
      name: 'Definition',
      state: revise,
      feedback:
          'Statement is hedge-only or lacks a verb+object after removing '
          'maybe/somehow/stuff/things. Name a specific action and its object.',
    );
  }
  return GateResult(
    name: 'Definition',
    state: pass,
    feedback: 'Statement is concrete enough to scrutinize (length, verb+object).',
  );
}

GateResult gateEvidence(Proposal p) {
  final items = p.evidence.where((e) => e.trim().isNotEmpty).toList();
  if (items.isEmpty) {
    return GateResult(
      name: 'Evidence',
      state: revise,
      feedback:
          'Evidence list is empty. Identify at least one fact, datum, or '
          'observation that grounds the statement.',
    );
  }
  return GateResult(
    name: 'Evidence',
    state: pass,
    feedback: '${items.length} evidence item(s) identified.',
  );
}

GateResult gateImpact(Proposal p) {
  final pos = p.impactsPositive.where((e) => e.trim().isNotEmpty).toList();
  final neg = p.impactsNegative.where((e) => e.trim().isNotEmpty).toList();
  final missing = <String>[];
  if (pos.isEmpty) missing.add('positive');
  if (neg.isEmpty) missing.add('negative');
  if (missing.isNotEmpty) {
    return GateResult(
      name: 'Impact',
      state: revise,
      feedback:
          'Impact list(s) empty: ${missing.join(' and ')}. Name who or what '
          'is affected on both the positive and the negative side.',
    );
  }
  return GateResult(
    name: 'Impact',
    state: pass,
    feedback: '${pos.length} positive and ${neg.length} negative impact(s) named.',
  );
}

String? _constraintPayload(String constraint) {
  var text = constraint.toLowerCase().split(RegExp(r'\s+')).join(' ');
  if (text.isEmpty) return null;
  var found = false;
  var remainder = ' $text ';
  for (final marker in negationMarkers) {
    final padded = marker.startsWith(' ') ? marker : ' $marker';
    if (remainder.contains(padded) || remainder.trimLeft().startsWith(marker)) {
      found = true;
      remainder = remainder.replaceAll(padded, ' ');
      final trimmed = remainder.trimLeft();
      if (trimmed.startsWith(marker)) {
        remainder = ' ${trimmed.substring(marker.length)}';
      }
    }
  }
  final payload = remainder.split(RegExp(r'\s+')).where((s) => s.isNotEmpty).join(' ');
  if (found && payload.isNotEmpty) return payload;
  return null;
}

bool statementContradicts(String statement, String constraint) {
  final payload = _constraintPayload(constraint);
  if (payload == null) return false;
  final hay = statement.toLowerCase().split(RegExp(r'\s+')).join(' ');
  return hay.contains(payload);
}

GateResult gateIntegrity(Proposal p) {
  final values = p.values.where((e) => e.trim().isNotEmpty).toList();
  if (values.isEmpty) {
    return GateResult(
      name: 'Integrity',
      state: revise,
      feedback:
          'Values list is empty. Integrity requires stated values so the '
          'proposal can be checked against them.',
    );
  }
  final hits = <String>[];
  for (final c in p.constraints) {
    if (statementContradicts(p.statement, c)) hits.add(c);
  }
  if (hits.isNotEmpty) {
    return GateResult(
      name: 'Integrity',
      state: block,
      feedback:
          'Statement contradicts a provided constraint (${hits.first}). '
          'A contradiction of this kind cannot pass Integrity without '
          'changing the proposal\'s nature.',
    );
  }
  return GateResult(
    name: 'Integrity',
    state: pass,
    feedback:
        '${values.length} value(s) stated; no constraint contradiction detected.',
  );
}

GateResult gateResponsibility(Proposal p) {
  final owner = p.accountablePerson.trim();
  if (owner.isEmpty) {
    return GateResult(
      name: 'Responsibility',
      state: block,
      feedback:
          'Accountable person is blank. Diffuse or absent ownership cannot '
          'pass Responsibility. Name one accountable owner.',
    );
  }
  return GateResult(
    name: 'Responsibility',
    state: pass,
    feedback: 'Accountable owner named: $owner.',
  );
}

Report runGates(Proposal raw) {
  final p = raw.normalized();
  final fns = [
    gateDefinition,
    gateEvidence,
    gateImpact,
    gateIntegrity,
    gateResponsibility,
  ];
  final lineage = <GateResult>[];
  var finalState = pass;
  String? blockedAt;
  for (final fn in fns) {
    final result = fn(p);
    lineage.add(result);
    if (result.state != pass) {
      finalState = result.state;
      if (result.state == block) blockedAt = result.name;
      break;
    }
  }
  return Report(lineage: lineage, finalState: finalState, blockedAt: blockedAt);
}

List<String> splitLines(String text) => text
    .replaceAll('\r\n', '\n')
    .split(RegExp(r'[\n;]'))
    .map((s) => s.trim())
    .where((s) => s.isNotEmpty)
    .toList();
