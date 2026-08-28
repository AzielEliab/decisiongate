import 'package:flutter/material.dart';

import 'gates.dart';
import 'theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const DecisionGateApp());
}

class DecisionGateApp extends StatelessWidget {
  const DecisionGateApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DecisionGATE',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const FormPage(),
    );
  }
}

class FormPage extends StatefulWidget {
  const FormPage({super.key});

  @override
  State<FormPage> createState() => _FormPageState();
}

class _FormPageState extends State<FormPage> {
  final _statement = TextEditingController();
  final _evidence = TextEditingController();
  final _pos = TextEditingController();
  final _neg = TextEditingController();
  final _values = TextEditingController();
  final _constraints = TextEditingController();
  final _owner = TextEditingController();

  @override
  void dispose() {
    _statement.dispose();
    _evidence.dispose();
    _pos.dispose();
    _neg.dispose();
    _values.dispose();
    _constraints.dispose();
    _owner.dispose();
    super.dispose();
  }

  void _run() {
    final report = runGates(Proposal(
      statement: _statement.text,
      evidence: splitLines(_evidence.text),
      impactsPositive: splitLines(_pos.text),
      impactsNegative: splitLines(_neg.text),
      values: splitLines(_values.text),
      constraints: splitLines(_constraints.text),
      accountablePerson: _owner.text,
    ));
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => ResultPage(report: report),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('DecisionGATE')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            motto,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: kGold,
                  fontStyle: FontStyle.italic,
                ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Five sequential gates. First failure stops the chain. '
            'PASS is clearance that the proposal survived scrutiny, not a '
            'suggestion to act. Offline. No analytics.',
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _statement,
            maxLines: 4,
            decoration: const InputDecoration(
              labelText: '1. Definition — concrete statement',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _evidence,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: '2. Evidence (one item per line)',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _pos,
            maxLines: 2,
            decoration: const InputDecoration(
              labelText: '3a. Impact — positive',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _neg,
            maxLines: 2,
            decoration: const InputDecoration(
              labelText: '3b. Impact — negative',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _values,
            decoration: const InputDecoration(
              labelText: '4. Integrity — values (line or ; separated)',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _constraints,
            decoration: const InputDecoration(
              labelText: '4b. Constraints (optional prohibitions)',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _owner,
            decoration: const InputDecoration(
              labelText: '5. Responsibility — accountable owner',
            ),
          ),
          const SizedBox(height: 20),
          FilledButton(
            onPressed: _run,
            child: const Text('Run gates'),
          ),
        ],
      ),
    );
  }
}

class ResultPage extends StatelessWidget {
  const ResultPage({super.key, required this.report});
  final Report report;

  Color _color(String state) {
    switch (state) {
      case pass:
        return const Color(0xFF3D8B5F);
      case revise:
        return const Color(0xFFC9A227);
      case block:
        return const Color(0xFFB54A4A);
      default:
        return kIvory;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Lineage')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            motto,
            style: Theme.of(context)
                .textTheme
                .bodyLarge
                ?.copyWith(color: kGold, fontStyle: FontStyle.italic),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'Final: ${report.finalState}'
                '${report.blockedAt != null ? '  blocked at ${report.blockedAt}' : ''}',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      color: _color(report.finalState),
                    ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Later gates are not evaluated after a failure.',
            style: TextStyle(fontStyle: FontStyle.italic),
          ),
          const SizedBox(height: 12),
          for (final g in report.lineage)
            Card(
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: _color(g.state),
                  child: Text(
                    g.state[0],
                    style: const TextStyle(color: kMatteBlack),
                  ),
                ),
                title: Text('${g.name} — ${g.state}'),
                subtitle: Text(g.feedback),
                isThreeLine: true,
              ),
            ),
        ],
      ),
    );
  }
}
